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

        with context.create('routing.olsr') as olsr_context:
            self.logger.info("Parsing olsrd information...")
            olsr_info = olsr_parser.OlsrInfo(
                host=settings.OLSRD_MONITOR_HOST,
                port=settings.OLSRD_MONITOR_PORT,
            )

            try:
                olsr_context.topology = olsr_info.get_topology()
                olsr_context.announces = olsr_info.get_announces()
                olsr_context.aliases = olsr_info.get_aliases()
            except olsr_parser.OlsrParseFailed:
                self.logger.warning("Failed to parse olsrd feeds!")
                return context, nodes

            # Create a mapping from router ids to nodes
            self.logger.info("Mapping router IDs to node instances...")
            visible_routers = set(olsr_context.topology.keys())
            registered_routers = set()
            olsr_context.router_id_map = {}
            for node in core_models.Node.objects.regpoint('config').registry_fields(
                router_id='core.routerid#router_id'
            ).registry_filter(
                core_routerid__rid_family='ipv4',
                core_routerid__router_id__in=visible_routers,
            ):
                first_router_id = node.router_id.all()[0]
                olsr_context.router_id_map[first_router_id] = node.pk
                registered_routers.add(first_router_id)
                nodes.add(node)

            self.logger.info("Creating unknown node instances...")
            for router_id in visible_routers.difference(registered_routers):
                # Create an invalid node for each unknown router id seen by olsrd
                node, created = core_models.Node.objects.get_or_create(
                    uuid=str(uuid.uuid5(olsr_models.OLSR_UUID_NAMESPACE, router_id))
                )
                nodes.add(node)
                olsr_context.router_id_map[router_id] = node.pk

                if created:
                    general_cfg = node.config.core.general(create=core_models.GeneralConfig)
                    # Name the nodes using their IP address by default
                    general_cfg.name = str(router_id)
                    general_cfg.save()

                    node.config.core.routerid(
                        create=core_models.StaticIpRouterIdConfig,
                        address='%s/32' % router_id,
                    ).save()

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

        if not context.push.source:
            # The processor is being invoked in global context. In this case, the GlobalTopology
            # processor has already provided information about the topology.
            try:
                rtm.router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
            except core_models.RouterIdConfig.DoesNotExist:
                # No router-id for this node can be found for IPv4. This means we can't identify the node.
                pass

            neighbours = context.routing.olsr.topology.get(rtm.router_id, [])
            announces = context.routing.olsr.announces.get(rtm.router_id, [])
            aliases = context.routing.olsr.aliases.get(rtm.router_id, [])
            push = False

            if not neighbours:
                version = 0
                context.node_available = False
            else:
                version = 1
                context.node_available = True
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
