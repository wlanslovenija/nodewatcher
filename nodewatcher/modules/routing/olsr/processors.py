import uuid

from django.conf import settings
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors, events as monitor_events
from nodewatcher.utils import ipaddr

from . import models as olsr_models, parser as olsr_parser


class GlobalTopology(monitor_processors.NetworkProcessor):
    """
    Processor that handles monitoring of olsrd routing daemon.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        self.logger.info("Parsing olsrd information...")
        olsr_info = olsr_parser.OlsrParser(
            host=getattr(settings, 'OLSRD_MONITOR_HOST', '127.0.0.1'),
            port=getattr(settings, 'OLSRD_MONITOR_PORT', 2006),
        )

        try:
            topology = olsr_info.get_topology()
            announces = olsr_info.get_announces()
            aliases = olsr_info.get_aliases()
        except olsr_parser.OlsrParseFailed:
            self.logger.warning("Failed to parse olsrd feeds!")
            return context, nodes

        # Create a mapping from router ids to nodes.
        self.logger.info("Mapping router IDs to node instances...")
        visible_routers = set(topology.keys())
        registered_routers = set()
        router_id_map = {}
        for node in core_models.Node.objects.regpoint('config').registry_fields(
            router_id='core.routerid__router_id'
        ).registry_filter(
            core_routerid__rid_family='ipv4',
            core_routerid__router_id__in=visible_routers,
        ):
            # In case there are multiple router IDs, select the one which is advertised by OLSR.
            first_router_id = node.router_id.filter(router_id__in=visible_routers)[0]
            router_id_map[first_router_id] = node.pk
            registered_routers.add(first_router_id)
            nodes.add(node)

            # Store per-node routing data.
            olsr_data = context.for_node[node.pk].routing.olsr
            olsr_data.router_id = first_router_id
            olsr_data.neighbours = topology.get(first_router_id, [])
            olsr_data.announces = announces.get(first_router_id, [])
            olsr_data.aliases = aliases.get(first_router_id, [])

        self.logger.info("Creating unknown node instances...")
        for router_id in visible_routers.difference(registered_routers):
            # Create an invalid node for each unknown router id seen by olsrd.
            node, created = core_models.Node.objects.get_or_create(
                uuid=str(uuid.uuid5(olsr_models.OLSR_UUID_NAMESPACE, router_id))
            )
            nodes.add(node)
            router_id_map[router_id] = node.pk

            # Store per-node routing data.
            olsr_data = context.for_node[node.pk].routing.olsr
            olsr_data.router_id = first_router_id
            olsr_data.neighbours = topology.get(first_router_id, [])
            olsr_data.announces = announces.get(first_router_id, [])
            olsr_data.aliases = aliases.get(first_router_id, [])

            if created:
                general_cfg = node.config.core.general(create=core_models.GeneralConfig)
                # Name the nodes using their IP address by default.
                general_cfg.name = str(router_id)
                general_cfg.save()

                node.config.core.routerid(
                    create=core_models.StaticIpRouterIdConfig,
                    address='%s/32' % router_id,
                ).save()

        # Prepare smaller router ID maps for each node.
        for router_id, neighbours in topology.iteritems():
            node_id = router_id_map[router_id]
            olsr_data = context.for_node[node_id].routing.olsr

            for neighbour in neighbours:
                address = str(neighbour['address'])
                olsr_data.router_id_map[address] = router_id_map[address]

        return context, nodes


class NodeTopology(monitor_processors.NodeProcessor):
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # In case the topology processor is included multiple times, do not re-process the
        # topology information. This may happen because this processor can be used in pull and
        # push contexts where the data source is different.
        if context.routing.olsr.node_topology_processed:
            return context
        context.routing.olsr.node_topology_processed = True

        try:
            rtm = node.monitoring.network.routing.topology(onlyclass=olsr_models.OlsrRoutingTopologyMonitor)[0]
        except IndexError:
            rtm = node.monitoring.network.routing.topology(
                create=olsr_models.OlsrRoutingTopologyMonitor,
                protocol=olsr_models.OLSR_PROTOCOL_NAME,
            )
            rtm.save()

        rtm.router_id = None
        rtm.average_lq = None
        rtm.average_ilq = None
        rtm.average_etx = None
        rtm.link_count = 0

        if not context.push.source:
            # The processor is being invoked in global context. In this case, the GlobalTopology
            # processor has already provided information about the topology.
            neighbours = context.routing.olsr.neighbours
            announces = context.routing.olsr.announces
            aliases = context.routing.olsr.aliases
            push = False

            if not neighbours:
                version = 0
            else:
                version = 1
                context.node_available = True

                rtm.router_id = context.routing.olsr.router_id
                aliases.append(rtm.router_id)

                # Update last seen timestamp as the router is at least visible.
                general = node.monitoring.core.general(create=monitor_models.GeneralMonitor)
                general.last_seen = timezone.now()
                general.save()
        else:
            # The processor is being invoked in push context. In this case, topology information
            # comes in via the telemetry.
            version = context.http.get_module_version('core.routing.olsr')
            push = True

            if version >= 1:
                rtm.router_id = context.http.core.routing.olsr.router_id
                neighbours = context.http.core.routing.olsr.neighbours
                announces = context.http.core.routing.olsr.exported_routes
                aliases = context.http.core.routing.olsr.link_local

        visible_lladdr = []
        visible_links = []
        visible_announces = []

        if version >= 1:
            # A list of link-local addresses of OLSR interfaces. This is required in order to be
            # able to generate a combined topology in case of push mode.
            for address in aliases:
                if isinstance(address, ipaddr.IPv4Address):
                    interface = None
                else:
                    try:
                        address, interface = address.split('%')
                    except ValueError:
                        interface = None

                    address = ipaddr.IPv4Address(address)

                lladdr, created = rtm.link_local.get_or_create(address=address)
                lladdr.interface = interface
                lladdr.save()
                visible_lladdr.append(lladdr)

            # Neighbours.
            for neighbour in neighbours:
                if not push:
                    try:
                        dst_node = core_models.Node.objects.get(
                            pk=context.routing.olsr.router_id_map.get(str(neighbour['address']), None)
                        )
                    except core_models.Node.DoesNotExist:
                        # Skip unknown neighbour.
                        self.logger.warning("Inconsistency in topology table for router ID %s!" % neighbour['address'])
                        continue
                else:
                    # Attempt to resolve destination node.
                    try:
                        lladdr = olsr_models.LinkLocalAddress.objects.get(address=neighbour['address'])
                    except olsr_models.LinkLocalAddress.DoesNotExist:
                        # Skip unknown neighbour.
                        continue

                    dst_node = lladdr.router.root

                elink, created = olsr_models.OlsrTopologyLink.objects.get_or_create(monitor=rtm, peer=dst_node)
                elink.lq = neighbour['lq']
                elink.ilq = neighbour['ilq']
                elink.etx = neighbour['cost']
                if push:
                    # In push mode, link cost is reported as an integer.
                    elink.etx = float(elink.etx) / 1024
                elink.last_seen = timezone.now()
                elink.save()
                visible_links.append(elink)

                if created:
                    # TODO: This will still create one event for each end of the link.
                    monitor_events.TopologyLinkEstablished(node, dst_node, olsr_models.OLSR_PROTOCOL_NAME).post()

            # Compute average values.
            if visible_links:
                rtm.average_lq = float(sum([link.lq for link in visible_links])) / len(visible_links)
                rtm.average_ilq = float(sum([link.ilq for link in visible_links])) / len(visible_links)
                rtm.average_etx = float(sum([link.etx for link in visible_links])) / len(visible_links)

            rtm.link_count = len(visible_links)
            rtm.save()

            # Create streams for all links.
            context.datastream.olsr_links = visible_links

            # Setup networks in announce tables.
            for announce in announces:
                eannounce, created = olsr_models.OlsrRoutingAnnounceMonitor.objects.get_or_create(
                    root=node,
                    network=announce['dst_prefix'],
                )
                eannounce.status = 'ok'
                eannounce.last_seen = timezone.now()
                eannounce.save()
                visible_announces.append(eannounce)

        # Remove all link-local addresses that do not exist anymore.
        rtm.link_local.exclude(pk__in=[x.pk for x in visible_lladdr]).delete()
        # Remove all links that do not exist anymore.
        rtm.links.exclude(pk__in=[x.pk for x in visible_links]).delete()
        # Remove all announces that do not exist anymore.
        node.monitoring.network.routing.announces(
            onlyclass=olsr_models.OlsrRoutingAnnounceMonitor, queryset=True
        ).exclude(pk__in=[x.pk for x in visible_announces]).delete()

        rtm.save()

        return context
