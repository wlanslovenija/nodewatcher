from django.conf import settings
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.monitor import models as monitor_models
from nodewatcher.monitor import processors as monitor_processors
from nodewatcher.legacy.nodes import models as nodes_models
from nodewatcher.routing_olsr import parser as olsr_parser
from nodewatcher.routing_olsr import models as olsr_models

class OLSRTopology(monitor_processors.NetworkProcessor):
    """
    Processor that handles monitoring of olsrd routing daemon.
    """
    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors.

        @param context: Current context
        @param nodes: A set of nodes that are to be processed
        @return: A (possibly) modified context and a (possibly) modified set of nodes
        """
        with context.in_namespace("routing"):
            with context.in_namespace("olsr"):
                self.logger.info("Parsing olsrd information...")
                olsr_info = olsr_parser.OlsrInfo(host = settings.OLSRD_MONITOR_HOST,
                                                 port = settings.OLSRD_MONITOR_PORT)

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
                for node in nodes_models.Node.objects.regpoint("config")\
                .registry_fields(router_id = "RouterIdConfig.router_id")\
                .filter(
                  routeridconfig_family = "ipv4",
                  routeridconfig_router_id__in = visible_routers
                ):
                    context.router_id_map[node.router_id] = node
                    registered_routers.add(node.router_id)
                    nodes.add(node)

                self.logger.info("Creating unknown node instances...")
                for router_id in visible_routers.difference(registered_routers):
                    # Create an invalid node for each unknown router id seen by olsrd
                    node = nodes_models.Node()
                    node.save()
                    nodes.add(node)
                    context.router_id_map[router_id] = node

                    rid_cfg = node.config.core.routerid(create = core_models.RouterIdConfig)
                    rid_cfg.router_id = router_id
                    rid_cfg.family = "ipv4"
                    rid_cfg.save()

                    status_mon = node.monitoring.core.status(create = monitor_models.StatusMonitor)
                    status_mon.status = "invalid"
                    status_mon.save()

        return context, nodes

class OLSRNodePostprocess(monitor_processors.NodeProcessor):
    def process(self, context, node):
        """
        Called for every processed node.

        @param context: Current context
        @param node: Node that is being processed
        @return: A (possibly) modified context
        """
        try:
            router_id = node.config.core.routerid(queryset = True).get(family = "ipv4").router_id
            topology = context.routing.olsr.topology.get(router_id, [])
            announces = context.routing.olsr.announces.get(router_id, [])
            aliases = context.routing.olsr.aliases.get(router_id, [])

            # Setup links in topology tables
            try:
                rtm = node.monitoring.network.routing.topology(onlyclass = olsr_models.OlsrRoutingTopologyMonitor)[0]
            except IndexError:
                rtm = node.monitoring.network.routing.topology(create = olsr_models.OlsrRoutingTopologyMonitor)
                rtm.save()

            if not topology:
                self.logger.warning("Empty topology entry for router ID %s!" % router_id)

            visible_links = []
            for link in topology:
                dst_node = context.routing.olsr.router_id_map.get(str(link['dst']), None)
                if not dst_node:
                    self.logger.warning("Inconsistency in topology table for router ID %s!" % link['dst'])
                    continue

                try:
                    elink = rtm.links.get(peer = dst_node)
                except monitor_models.TopologyLink.DoesNotExist:
                    elink = olsr_models.OlsrTopologyLink(monitor = rtm, peer = dst_node)

                elink.lq = link['lq']
                elink.ilq = link['ilq']
                elink.etx = link['etx']
                elink.last_seen = timezone.now()
                elink.save()
                visible_links.append(elink)

            # Remove all links that do not exist anymore
            rtm.links.exclude(pk__in = [x.pk for x in visible_links]).delete()

            # Setup networks in announce tables
            visible_announces = []
            existing_announces = node.monitoring.network.routing.announces(
              onlyclass = olsr_models.OlsrRoutingAnnounceMonitor, queryset = True)
            for announce in announces + aliases:
                network = announce['net'] if 'net' in announce else announce['alias']
                try:
                    eannounce = existing_announces.get(network = network)
                except monitor_models.RoutingAnnounceMonitor.DoesNotExist:
                    eannounce = olsr_models.OlsrRoutingAnnounceMonitor(root = node, network = network)

                eannounce.status = "ok" if 'net' in announce else "alias"
                eannounce.last_seen = timezone.now()
                eannounce.save()
                visible_announces.append(eannounce)

            # Remove all announces that do not exist anymore
            existing_announces.exclude(pk__in = [x.pk for x in visible_announces]).delete()
        except core_models.RouterIdConfig.DoesNotExist:
            # No router-id for this node can be found for IPv4; this means
            # that we have nothing to do here
            pass

        return context
