import uuid

from django.conf import settings
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors, events as monitor_events

from . import models as olsr_models, parser as olsr_parser


class Topology(monitor_processors.NetworkProcessor):
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

        with context.in_namespace('routing'):
            with context.in_namespace('olsr'):
                self.logger.info("Parsing olsrd information...")
                olsr_info = olsr_parser.OlsrInfo(
                    host=settings.OLSRD_MONITOR_HOST,
                    port=settings.OLSRD_MONITOR_PORT,
                )

                try:
                    context.topology = olsr_info.get_topology()
                    context.announces = olsr_info.get_announces()
                    context.aliases = olsr_info.get_aliases()
                except olsr_parser.OlsrParseFailed:
                    self.logger.warning("Failed to parse olsrd feeds!")
                    return context, nodes

                # Create a mapping from router ids to nodes
                self.logger.info("Mapping router IDs to node instances...")
                visible_routers = set(context.topology.keys())
                registered_routers = set()
                context.router_id_map = {}
                for node in core_models.Node.objects.regpoint('config').registry_fields(
                    router_id='core.routerid#router_id'
                ).registry_filter(
                    core_routerid__rid_family='ipv4',
                    core_routerid__router_id__in=visible_routers,
                ):
                    context.router_id_map[node.router_id[0]] = node
                    registered_routers.add(node.router_id[0])
                    nodes.add(node)

                self.logger.info("Creating unknown node instances...")
                for router_id in visible_routers.difference(registered_routers):
                    # Create an invalid node for each unknown router id seen by olsrd
                    node, created = core_models.Node.objects.get_or_create(
                        uuid=str(uuid.uuid5(olsr_models.OLSR_UUID_NAMESPACE, router_id))
                    )
                    nodes.add(node)
                    context.router_id_map[router_id] = node

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


class NodePostprocess(monitor_processors.NodeProcessor):
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        try:
            router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
            topology = context.routing.olsr.topology.get(router_id, [])
            announces = context.routing.olsr.announces.get(router_id, [])
            aliases = context.routing.olsr.aliases.get(router_id, [])

            if not topology:
                context.node_available = False
                return context
            else:
                context.node_available = True

            # Update last seen timestamp as the router is at least visible
            general = node.monitoring.core.general(create=monitor_models.GeneralMonitor)
            general.last_seen = timezone.now()
            general.save()

            # Setup links in topology tables
            try:
                rtm = node.monitoring.network.routing.topology(onlyclass=olsr_models.OlsrRoutingTopologyMonitor)[0]
            except IndexError:
                rtm = node.monitoring.network.routing.topology(
                    create=olsr_models.OlsrRoutingTopologyMonitor,
                    protocol=olsr_models.OLSR_PROTOCOL_NAME,
                )
                rtm.save()

            visible_links = []
            for link in topology:
                dst_node = context.routing.olsr.router_id_map.get(str(link['dst']), None)
                if not dst_node:
                    self.logger.warning("Inconsistency in topology table for router ID %s!" % link['dst'])
                    continue

                elink, created = olsr_models.OlsrTopologyLink.objects.get_or_create(monitor=rtm, peer=dst_node)
                elink.lq = link['lq']
                elink.ilq = link['ilq']
                elink.etx = link['etx']
                elink.last_seen = timezone.now()
                elink.save()
                visible_links.append(elink)

                if created:
                    # TODO: This will still create one event for each end of the link
                    # TODO: We should probably have a history of adjancencies (as in v2) to avoid repeating these events
                    monitor_events.TopologyLinkEstablished(node, dst_node, olsr_models.OLSR_PROTOCOL_NAME).post()

            # Compute average values
            if visible_links:
                rtm.average_lq = float(sum([link.lq for link in visible_links])) / len(visible_links)
                rtm.average_ilq = float(sum([link.ilq for link in visible_links])) / len(visible_links)
                rtm.average_etx = float(sum([link.etx for link in visible_links])) / len(visible_links)
            else:
                rtm.average_lq = None
                rtm.average_ilq = None
                rtm.average_etx = None
            rtm.link_count = len(visible_links)
            rtm.save()

            # Create streams for all links
            context.datastream.olsr_links = visible_links

            # Remove all links that do not exist anymore
            rtm.links.exclude(pk__in=[x.pk for x in visible_links]).delete()

            # Setup networks in announce tables
            visible_announces = []
            existing_announces = node.monitoring.network.routing.announces(
                onlyclass=olsr_models.OlsrRoutingAnnounceMonitor, queryset=True
            )
            for announce in announces + aliases:
                network = announce['net'] if 'net' in announce else announce['alias']
                eannounce, created = olsr_models.OlsrRoutingAnnounceMonitor.objects.get_or_create(root=node, network=network)
                eannounce.status = "ok" if 'net' in announce else "alias"
                eannounce.last_seen = timezone.now()
                eannounce.save()
                visible_announces.append(eannounce)

            # Remove all announces that do not exist anymore
            existing_announces.exclude(pk__in=[x.pk for x in visible_announces]).delete()
        except core_models.RouterIdConfig.DoesNotExist:
            # No router-id for this node can be found for IPv4; this means
            # that we have nothing to do here
            pass

        return context
