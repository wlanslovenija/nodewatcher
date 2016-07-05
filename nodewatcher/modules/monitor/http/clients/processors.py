import datetime
import pytz

from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import ipaddr
from nodewatcher.modules.monitor.sources.http import processors as http_processors

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class ClientStreams(ds_models.RegistryRootStreams):
        client_count = ds_fields.IntegerField(tags={
            'title': gettext_noop("Client count"),
            'description': gettext_noop("Number of clients connected to the node."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
            },
        })

        def get_module_name(self):
            return 'monitor.http.clients'

    class ClientStreamsData(object):
        def __init__(self, node, client_count):
            self.node = node
            self.client_count = client_count

    ds_pool.register(ClientStreamsData, ClientStreams)

    DATASTREAM_SUPPORTED = True
except ImportError:
    pass


class ClientInfo(monitor_processors.NodeProcessor):
    """
    Stores node's reported connected clients into the monitoring schema. Will
    only run if HTTP monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context('http', http_processors.HTTPTelemetryContext)
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

        version = context.http.get_module_version('core.clients')
        if version == 0:
            # Unsupported version or data fetch failed (v0)
            return context

        client_count = 0
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
            client_count += 1

            del existing_clients[client_id]

        for client in existing_clients.values():
            client.delete()

        if DATASTREAM_SUPPORTED:
            # Store client count into datastream.
            context.datastream.monitor_http_clients = ClientStreamsData(node, client_count)

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
