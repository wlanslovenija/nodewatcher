from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors
from nodewatcher.utils import ipaddr

from . import models


class KoruzaVpn(monitor_processors.NodeProcessor):
    """
    Stores KORUZA VPN monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http", http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        version = context.http.get_module_version('koruza.vpn')

        koruza_vpn = node.monitoring.koruza.vpn(create=models.KoruzaVpnMonitor)
        koruza_vpn.ip_address = None

        if version >= 1:
            koruza_vpn.ip_address = ipaddr.IPNetwork(context.http.koruza.vpn.ip)

        koruza_vpn.save()

        return context
