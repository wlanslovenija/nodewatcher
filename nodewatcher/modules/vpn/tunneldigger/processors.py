from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.core.generator.cgm import models as cgm_models

from . import models

DATASTREAM_SUPPORTED = True
try:
    from django_datastream import datastream
    from nodewatcher.modules.monitor.datastream import base as ds_base, fields as ds_fields
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


    class TunneldiggerStreams(ds_base.StreamsBase):
        tx_bytes_rate = ds_fields.DynamicSumField()
        rx_bytes_rate = ds_fields.DynamicSumField()

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
except ImportError:
    DATASTREAM_SUPPORTED = False


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

        if DATASTREAM_SUPPORTED:
            # Include a dummy model so that the datastream processor will generate
            # streams for it
            context.datastream.tunneldigger = TunneldiggerStreamsData(node)
            td_streams = ds_pool.get_descriptor(context.datastream.tunneldigger)

            # Initialize all dynamic sum fields to have no sources
            for field in td_streams.get_fields():
                field.clear_source_fields()

        # Verify that configured tunneldigger interfaces are present
        for idx, interface in enumerate(node.config.core.interfaces(onlyclass=cgm_models.VpnInterfaceConfig)):
            if interface.protocol != 'tunneldigger':
                continue

            # TODO: Should we identify VPN interfaces based on configured MAC address?
            ifname = models.get_tunneldigger_interface_name(idx)
            try:
                iface = node.monitoring.core.interfaces(queryset=True).get(name=ifname).cast()
                if DATASTREAM_SUPPORTED:
                    iface_streams = ds_pool.get_descriptor(iface)
                    
                    if iface_streams is not None:
                        for dst_field in td_streams.get_fields():
                            src_field = getattr(iface_streams, dst_field.name, None)
                            if src_field is None:
                                continue

                            # Hide source field from being displayed by default
                            src_field.set_tags(visualization={'hidden': True})
                            # Include this field into our general summed field
                            dst_field.add_source_field(src_field, iface_streams)
            except monitor_models.InterfaceMonitor.DoesNotExist:
                # TODO: Generate an event that digger interface does not exist
                continue

        return context
