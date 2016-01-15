from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors

from . import models

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class TunneldiggerStreams(ds_models.RegistryRootStreams):
        tx_bytes = ds_fields.CounterField()
        tx_bytes_rate = ds_fields.RateField("system.status#reboots", "#tx_bytes", tags={
            'group': 'tunneldigger_bytes_rate',
            'title': gettext_noop("Tunneldigger TX bytes rate"),
            'description': gettext_noop("Combined throughput of transmitted packets via Tunneldigger."),
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
        rx_bytes = ds_fields.CounterField()
        rx_bytes_rate = ds_fields.RateField("system.status#reboots", "#rx_bytes", tags={
            'group': 'tunneldigger_bytes_rate',
            'title': gettext_noop("Tunneldigger RX bytes rate"),
            'description': gettext_noop("Combined throughput of received packets via Tunneldigger."),
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

        def get_module_name(self):
            return 'vpn.tunneldigger'

    class TunneldiggerStreamsData(object):
        def __init__(self, node):
            self.node = node
            self.tx_bytes = None
            self.rx_bytes = None

        def add(self, interface):
            # Update TX bytes.
            if interface.tx_bytes is not None:
                if self.tx_bytes is None:
                    self.tx_bytes = 0

                self.tx_bytes += interface.tx_bytes

            # Update RX bytes.
            if interface.rx_bytes is not None:
                if self.rx_bytes is None:
                    self.rx_bytes = 0

                self.rx_bytes += interface.rx_bytes

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

        # Verify that configured tunneldigger interfaces are present.
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

            # Include a dummy model so that the datastream processor will generate streams for it.
            context.datastream.tunneldigger = TunneldiggerStreamsData(node)
            self.td_streams = ds_pool.get_descriptor(context.datastream.tunneldigger)

            return super(DatastreamTunneldigger, self).process(context, node)

        def process_interface(self, context, iface):
            """
            Performs per-interface processing.
            """

            super(DatastreamTunneldigger, self).process_interface(context, iface)

            # Sum all counters to get the value for all VPN interfaces.
            context.datastream.tunneldigger.add(iface)

            # Modify underlying interface streams.
            iface_streams = ds_pool.get_descriptor(iface)
            if iface_streams is not None:
                for dst_field in self.td_streams.get_fields():
                    src_field = getattr(iface_streams, dst_field.name, None)
                    if src_field is None:
                        continue

                    # Hide the source field from being displayed by default.
                    src_field.set_tags(visualization={'initial_set': False})
