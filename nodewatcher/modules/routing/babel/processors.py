from django.utils import timezone

from nodewatcher.core.monitor import processors as monitor_processors, events as monitor_events
from nodewatcher.modules.monitor.sources.http import processors as http_processors
from nodewatcher.utils import ipaddr

from . import models as babel_models


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

        if version >= 1:
            # Router ID.
            rtm.router_id = context.http.core.routing.babel.router_id
            # A list of link-local addresses of Babel interfaces. This is required in order to be
            # able to generate a combined topology.
            visible_lladdr = []
            for address in context.http.core.routing.babel.link_local:
                try:
                    address, interface = address.split('%')
                except ValueError:
                    interface = None

                lladdr, created = rtm.link_local.get_or_create(address=ipaddr.IPv6Address(address))
                lladdr.interface = interface
                lladdr.save()
                visible_lladdr.append(lladdr)

            # Remove all link-local addresses that do not exist anymore.
            rtm.link_local.exclude(pk__in=[x.pk for x in visible_lladdr]).delete()

            # Neighbours.
            visible_links = []
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

            # Remove all links that do not exist anymore.
            rtm.links.exclude(pk__in=[x.pk for x in visible_links]).delete()

            # Exported routes.
            visible_announces = []
            existing_announces = node.monitoring.network.routing.announces(
                onlyclass=babel_models.BabelRoutingAnnounceMonitor, queryset=True
            )
            for announce in context.http.core.routing.babel.exported_routes:
                eannounce, created = babel_models.BabelRoutingAnnounceMonitor.objects.get_or_create(
                    root=node,
                    network=announce['dst_prefix'],
                )
                eannounce.status = 'ok'
                eannounce.last_seen = timezone.now()
                eannounce.save()
                visible_announces.append(eannounce)

            # Remove all announces that do not exist anymore.
            existing_announces.exclude(pk__in=[x.pk for x in visible_announces]).delete()

        rtm.save()

        return context
