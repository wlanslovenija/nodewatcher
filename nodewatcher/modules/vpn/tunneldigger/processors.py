from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors

from . import models

DATASTREAM_SUPPORTED = False
try:
    from django_datastream import datastream
    from nodewatcher.modules.monitor.datastream import base as ds_base, fields as ds_fields
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class TunneldiggerStreams(ds_base.StreamsBase):
        tx_bytes_rate = ds_fields.DynamicSumField(tags={
            'group': 'tunneldigger_bytes_rate',
            'title': gettext_noop("VPN TX bytes rate"),
            'description': gettext_noop("Combined throughput of transmitted packets via VPN."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
                'with': {'group': 'tunneldigger_bytes_rate', 'node': ds_fields.TagReference('node')},
            },
            'unit': 'Bps',
        })
        rx_bytes_rate = ds_fields.DynamicSumField(tags={
            'group': 'tunneldigger_bytes_rate',
            'title': gettext_noop("VPN RX bytes rate"),
            'description': gettext_noop("Combined throughput of received packets via VPN."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
                'with': {'group': 'tunneldigger_bytes_rate', 'node': ds_fields.TagReference('node')},
            },
            'unit': 'Bps',
        })

        def get_stream_query_tags(self):
            return {'node': self._model.node.uuid, 'module': 'tunneldigger'}

        def get_stream_tags(self):
            return {'node': self._model.node.uuid, 'module': 'tunneldigger'}

        def get_stream_highest_granularity(self):
            return datastream.Granularity.Minutes

    class TunneldiggerStreamsData(object):
        def __init__(self, node):
            self.node = node

    ds_pool.register(TunneldiggerStreamsData, TunneldiggerStreams)

    DATASTREAM_SUPPORTED = True
except ImportError:
    pass


class Tunneldigger(monitor_processors.NodeProcessor):
    """
    Performs tunneldigger-related monitoring functions.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # Verify that configured tunneldigger interfaces are present
        for idx, interface in enumerate(node.config.core.interfaces(onlyclass=models.TunneldiggerInterfaceConfig)):
            # TODO: Should we identify VPN interfaces based on configured MAC address?
            ifname = models.get_tunneldigger_interface_name(idx)
            try:
                iface = node.monitoring.core.interfaces(queryset=True).get(name=ifname, up=True).cast()
                self.process_interface(context, iface)
            except monitor_models.InterfaceMonitor.DoesNotExist:
                # TODO: Generate an event that digger interface does not exist or is down.
                continue

        return context

    def process_interface(self, context, iface):
        """
        Performs per-interface processing.
        """

        pass


if DATASTREAM_SUPPORTED:
    class DatastreamTunneldigger(Tunneldigger):

        def process(self, context, node):
            """
            Called for every processed node.

            :param context: Current context
            :param node: Node that is being processed
            :return: A (possibly) modified context
            """

            # Include a dummy model so that the datastream processor will generate
            # streams for it
            context.datastream.tunneldigger = TunneldiggerStreamsData(node)
            self.td_streams = ds_pool.get_descriptor(context.datastream.tunneldigger)

            # Initialize all dynamic sum fields to have no sources
            for field in self.td_streams.get_fields():
                field.clear_source_fields()

            return super(DatastreamTunneldigger, self).process(context, node)

        def process_interface(self, context, iface):
            """
            Performs per-interface processing.
            """

            super(DatastreamTunneldigger, self).process_interface(context, iface)
            iface_streams = ds_pool.get_descriptor(iface)

            if iface_streams is not None:
                for dst_field in self.td_streams.get_fields():
                    src_field = getattr(iface_streams, dst_field.name, None)
                    if src_field is None:
                        continue

                    # Hide source field from being displayed by default
                    src_field.set_tags(visualization={'initial_set': False})
                    # Include this field into our general summed field
                    dst_field.add_source_field(src_field, iface_streams)
