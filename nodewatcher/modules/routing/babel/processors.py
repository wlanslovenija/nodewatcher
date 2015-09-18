from django.conf import settings
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors, events as monitor_events
from nodewatcher.modules.monitor.sources.http import processors as http_processors
from nodewatcher.utils import ipaddr

from . import models as babel_models, parser as babel_parser


class IncludeRoutableNodes(monitor_processors.NetworkProcessor):
    """
    Selects all nodes for which routes exist as reported by the local Babel daemon.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        # Fetch data from the Babel daemon.
        self.logger.info("Parsing babeld information...")
        babel = babel_parser.BabelParser(
            host=getattr(settings, 'BABELD_MONITOR_HOST', '::1'),
            port=getattr(settings, 'BABELD_MONITOR_PORT', 33123),
        )

        try:
            routes = babel.routes
        except babel_parser.BabelParseFailed:
            self.logger.warning("Failed to parse babeld feeds!")
            return context, nodes

        # Determine which nodes are available.
        for node in core_models.Node.objects.regpoint('config').registry_fields(
            router_id='core.routerid#router_id'
        ).registry_filter(
            core_routerid__rid_family__in=['ipv4', 'ipv6'],
        ):
            for router_id in node.router_id.all():
                # Try to find the most specific route for this router.
                route = routes.search_best(router_id)
                if route.prefixlen > 20:
                    nodes.add(node)

                    # A specific enough route exists for this node, count it as available.
                    context.for_node[node.pk].node_available = True
                    break

        return context, nodes


class BabelTopology(monitor_processors.NodeProcessor):
    """
    Stores Babel topology data into the database. Will only run if HTTP monitor
    module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http", http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        try:
            rtm = node.monitoring.network.routing.topology(onlyclass=babel_models.BabelRoutingTopologyMonitor)[0]
        except IndexError:
            rtm = node.monitoring.network.routing.topology(
                create=babel_models.BabelRoutingTopologyMonitor,
                protocol=babel_models.BABEL_PROTOCOL_NAME,
            )
            rtm.save()

        rtm.router_id = None
        rtm.average_rxcost = None
        rtm.average_txcost = None
        rtm.average_rttcost = None
        rtm.average_cost = None

        version = context.http.get_module_version('core.routing.babel')

        visible_lladdr = []
        visible_links = []
        visible_announces = []
        router_id = context.http.core.routing.babel.router_id

        if version >= 1 and router_id:
            # Router ID.
            rtm.router_id = router_id
            # A list of link-local addresses of Babel interfaces. This is required in order to be
            # able to generate a combined topology.
            for address in context.http.core.routing.babel.link_local:
                try:
                    address, interface = address.split('%')
                except ValueError:
                    interface = None

                lladdr, created = rtm.link_local.get_or_create(address=ipaddr.IPv6Address(address))
                lladdr.interface = interface
                lladdr.save()
                visible_lladdr.append(lladdr)

            # Neighbours.
            for neighbour in context.http.core.routing.babel.neighbours:
                # Attempt to resolve destination node.
                try:
                    lladdr = babel_models.LinkLocalAddress.objects.get(address=neighbour['address'])
                except babel_models.LinkLocalAddress.DoesNotExist:
                    # Skip unknown neighbour.
                    continue

                dst_node = lladdr.router.root

                elink, created = babel_models.BabelTopologyLink.objects.get_or_create(monitor=rtm, peer=dst_node)
                elink.interface = neighbour['interface']
                elink.rxcost = neighbour['rxcost']
                elink.txcost = neighbour['txcost']
                elink.reachability = neighbour['reachability']
                elink.rtt = neighbour.get('rtt', None)
                elink.rttcost = neighbour.get('rttcost', None)
                elink.cost = neighbour['cost']
                elink.last_seen = timezone.now()
                elink.save()
                visible_links.append(elink)

                if created:
                    # TODO: This will still create one event for each end of the link.
                    monitor_events.TopologyLinkEstablished(node, dst_node, babel_models.BABEL_PROTOCOL_NAME).post()

            # Compute average values.
            if visible_links:
                rtm.average_rxcost = float(sum([link.rxcost for link in visible_links])) / len(visible_links)
                rtm.average_txcost = float(sum([link.txcost for link in visible_links])) / len(visible_links)
                rtm.average_rttcost = float(sum([link.rttcost for link in visible_links if link.rttcost is not None])) / len(visible_links)
                rtm.average_cost = float(sum([link.cost for link in visible_links])) / len(visible_links)

            rtm.link_count = len(visible_links)
            rtm.save()

            # Create streams for all links.
            context.datastream.babel_links = visible_links

            # Exported routes.
            for announce in context.http.core.routing.babel.exported_routes:
                eannounce, created = babel_models.BabelRoutingAnnounceMonitor.objects.get_or_create(
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
            onlyclass=babel_models.BabelRoutingAnnounceMonitor, queryset=True
        ).exclude(pk__in=[x.pk for x in visible_announces]).delete()

        rtm.save()

        return context
