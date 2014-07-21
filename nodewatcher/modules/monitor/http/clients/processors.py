import datetime
import pytz

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import ipaddr


class ClientInfo(monitor_processors.NodeProcessor):
    """
    Stores node's reported connected clients into the monitoring schema. Will
    only run if HTTP monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http")
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        existing_clients = {}
        for client in node.monitoring.network.clients():
            existing_clients[client.client_id] = client

        version = context.http.get_module_version("core.clients")
        if version == 0:
            # Unsupported version or data fetch failed (v0)
            return context

        for client_id, data in context.http.core.clients.iteritems():
            if client_id.startswith('_'):
                continue

            try:
                client = existing_clients[client_id]
            except KeyError:
                client = node.monitoring.network.clients(create=monitor_models.ClientMonitor)
                client.client_id = client_id
                existing_clients[client_id] = client

            client.save()
            self.process_client(context, node, client, data)

            del existing_clients[client_id]

        for client in existing_clients.values():
            client.delete()

        return context

    def process_client(self, context, node, client, data):
        """
        Processes a single client descriptor.

        :param context: Current context
        :param node: Node that is being processed
        :param client: Client model
        :param data: Telemetry data
        """

        existing_addresses = {}
        for address in client.addresses.all():
            existing_addresses[address.address] = address

        for address in data.addresses:
            ip = ipaddr.IPNetwork(address['address'])
            client_address = existing_addresses.get(ip, None)
            if client_address is None:
                client_address, _ = client.addresses.get_or_create(
                    client=client,
                    address=ip,
                )

                existing_addresses[ip] = client_address

            client_address.expiry_time = datetime.datetime.fromtimestamp(
                int(address['expires']),
                pytz.utc
            )

            if address['family'] == 'ipv4':
                client_address.family = 'ipv4'
            elif address['family'] == 'ipv6':
                client_address.family = 'ipv6'
            else:
                self.logger.warning("Unknown network family '%s' on node '%s' client '%s'!" % (address['family'], node.pk, client.client_id))

            client_address.save()
            del existing_addresses[ip]

        for address in existing_addresses.values():
            address.delete()
