from django.utils.translation import gettext_noop

from django_datastream import datastream

# To create node.monitoring registration point
import nodewatcher.core.monitor
from nodewatcher.core.monitor import models

from . import base, fields
from .pool import pool


class RegistryItemStreams(base.StreamsBase):
    """
    Base class for registry item stream attributes.
    """

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        return {
            'node': self._model.root.uuid,
            'registry_id': self._model._registry.registry_id,
        }

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes

    def resolve_model_reference(self, model_reference):
        """
        Some fields support referencing other fields. In order to resolve
        model references, this method must be overriden. It should return
        the resolved model class.

        :param model_reference: String representing the model reference
        :return: Resolved model class
        """

        regpoint = self._model._registry.registration_point
        return getattr(self._model.root, regpoint.namespace).by_registry_id(model_reference)


class RegistryRootStreams(base.StreamsBase):
    """
    Base class for registry root stream attributes.
    """

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        return {
            'node': self.get_root().uuid,
            'module': self.get_module_name(),
        }

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes

    def resolve_model_reference(self, model_reference):
        """
        Some fields support referencing other fields. In order to resolve
        model references, this method must be overriden. It should return
        the resolved model class.

        :param model_reference: A string representing the model reference
        :return: Resolved model class
        """

        return getattr(
            self.get_root(),
            self.get_regpoint_namespace(model_reference)
        ).by_registry_id(model_reference)

    def get_regpoint_namespace(self, model_reference):
        """
        Returns the registration point namespace, which should be used to resolve
        the given model reference.

        :param model_reference: A string representing the model reference
        :return: Registration point namespace under the root model
        """

        return 'monitoring'

    def get_root(self):
        """
        Returns the root model that this proxy should operate on.

        :return: Root model instance
        """

        return self._model.node

    def get_module_name(self):
        """
        Returns the module name that should be used as part of the query tags.
        """

        raise NotImplementedError


class ProxyRegistryItemStreams(RegistryItemStreams):
    """
    A convenience class that can be used in models that reference
    registry items but are not registry items themselves.
    """

    class CombinedProxyModel(object):
        def __init__(self, *models):
            self.models = models

        def __getattr__(self, key):
            for mdl in self.models:
                try:
                    return getattr(mdl, key)
                except AttributeError:
                    continue

            raise AttributeError(key)

    def __init__(self, model):
        """
        Class constructor.
        """

        super(ProxyRegistryItemStreams, self).__init__(
            ProxyRegistryItemStreams.CombinedProxyModel(model, self.get_base(model))
        )

    def get_base(self, model):
        """
        Returns the base model that this proxy should operate on.

        :param model: Original model instance
        :return: Base model instance
        """

        return model


class SystemStatusMonitorStreams(RegistryItemStreams):
    uptime = fields.IntegerField(tags={
        'title': gettext_noop("Uptime"),
        'description': gettext_noop("Uptime of the node's system."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        },
        'unit': 's',
    })
    reboots = fields.ResetField("#uptime", tags={
        'title': gettext_noop("Reboots"),
        'description': gettext_noop("Node reboot events."),
        'label': gettext_noop("R"),
        'message': gettext_noop("Node reboot."),
        'visualization': {
            'type': 'event',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['count'],
            'with': {'node': fields.TagReference('node')},
        },
    })

pool.register(models.SystemStatusMonitor, SystemStatusMonitorStreams)


class GeneralResourcesMonitorStreams(RegistryItemStreams):
    loadavg_1min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (1 min)"),
        'description': gettext_noop("1 minute load average."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        },
    })
    loadavg_5min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (5 min)"),
        'description': gettext_noop("5 minute load average."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        },
    })
    loadavg_15min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (15 min)"),
        'description': gettext_noop("15 minute load average."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        },
    })
    memory_free = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Free memory"),
        'description': gettext_noop("Amount of free memory."),
        'visualization': {
            'type': 'stack',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        },
        'unit': 'B',
    })
    memory_buffers = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Buffers memory"),
        'description': gettext_noop("Amount of memory used for kernel buffers."),
        'visualization': {
            'type': 'stack',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        },
        'unit': 'B',
    })
    memory_cache = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Cache memory"),
        'description': gettext_noop("Amount of memory used for cache."),
        'visualization': {
            'type': 'stack',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        },
        'unit': 'B',
    })
    memory_total = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Total memory"),
        'description': gettext_noop("Total amount of memory."),
        'visualization': {
            'type': 'line',
            # We want total memory in graphs, but we hide it by the default to emphasise visualization on used memory.
            'initial_set': True,
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        },
        'unit': 'B',
    })
    processes = fields.IntegerField(tags={
        'title': gettext_noop("Processes"),
        'description': gettext_noop("Number of running processes."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
    })

pool.register(models.GeneralResourcesMonitor, GeneralResourcesMonitorStreams)


class NetworkResourcesMonitorStreams(RegistryItemStreams):
    routes = fields.IntegerField(tags={
        'title': gettext_noop("Routes"),
        'description': gettext_noop("Number of routes installed in the kernel routing tables."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
    })
    tcp_connections = fields.IntegerField(tags={
        'title': gettext_noop("TCP connections"),
        'description': gettext_noop("Number of local TCP connections."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
    })
    udp_connections = fields.IntegerField(tags={
        'title': gettext_noop("UDP connections"),
        'description': gettext_noop("Number of local UDP connections."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
    })
    track_connections = fields.IntegerField(tags={
        'group': 'track_connections',
        'title': gettext_noop("Tracked connections"),
        'description': gettext_noop("Number of tracked connections."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'track_connections', 'node': fields.TagReference('node')},
        },
    })
    track_connections_max = fields.IntegerField(tags={
        'group': 'track_connections',
        'title': gettext_noop("Tracked connections limit"),
        'description': gettext_noop("Limit of the number of tracked connections."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'track_connections', 'node': fields.TagReference('node')},
        },
    })

pool.register(models.NetworkResourcesMonitor, NetworkResourcesMonitorStreams)


class RttMeasurementMonitorStreams(RegistryItemStreams):
    packet_loss = fields.IntegerField(tags={
        'group': 'packet_loss',
        'title': fields.TagReference('packet_size', gettext_noop("Packet loss (%(packet_size)s bytes)")),
        'description': gettext_noop("Packet loss in percent."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 100.0,
            'with': {'group': 'packet_loss', 'node': fields.TagReference('node')},
        },
        'unit': '%',
    })
    rtt = fields.MultiPointField(
        tags={
            'group': 'rtt',
            'title': fields.TagReference('packet_size', gettext_noop("RTT (%(packet_size)s bytes)")),
            'description': gettext_noop("Measured round-trip time."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
                'with': {'group': 'rtt', 'node': fields.TagReference('node')},
            },
            'unit': 'ms',
        },
        value_downsamplers=['mean', 'sum', 'min', 'max', 'std_dev', 'count'],
        attribute=lambda model: {
            'c': model.successful_packets,
            'm': model.rtt_average,
            'l': model.rtt_minimum,
            'u': model.rtt_maximum,
            'd': model.rtt_std,
            's': model.rtt_average * model.successful_packets if model.rtt_average is not None else None,
            'q': (model.rtt_average ** 2 * model.successful_packets + (model.rtt_std ** 2) * (model.successful_packets - 1)) if model.rtt_std is not None else None,
        }
    )

    def get_stream_query_tags(self):
        tags = super(RttMeasurementMonitorStreams, self).get_stream_query_tags()
        tags.update({'packet_size': self._model.packet_size})
        return tags

pool.register(models.RttMeasurementMonitor, RttMeasurementMonitorStreams)


class InterfaceStreams(RegistryItemStreams):
    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        tags = super(InterfaceStreams, self).get_stream_query_tags()
        tags.update({'interface': self._model.name})
        return tags


class InterfaceMonitorStreams(InterfaceStreams):
    tx_packets = fields.CounterField()
    tx_packets_rate = fields.RateField("system.status#reboots", "#tx_packets", tags={
        'group': 'packets_rate',
        'title': fields.TagReference('interface', gettext_noop("TX packets rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmitted packets."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'packets_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'pps',
    })
    rx_packets = fields.CounterField()
    rx_packets_rate = fields.RateField("system.status#reboots", "#rx_packets", tags={
        'group': 'packets_rate',
        'title': fields.TagReference('interface', gettext_noop("RX packets rate (%(interface)s)")),
        'description': gettext_noop("Rate of received packets."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'packets_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'pps',
    })
    tx_bytes = fields.CounterField()
    tx_bytes_rate = fields.RateField("system.status#reboots", "#tx_bytes", tags={
        'group': 'bytes_rate',
        'title': fields.TagReference('interface', gettext_noop("TX bytes rate (%(interface)s)")),
        'description': gettext_noop("Throughput of transmitted packets."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'bytes_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Bps',
    })
    rx_bytes = fields.CounterField()
    rx_bytes_rate = fields.RateField("system.status#reboots", "#rx_bytes", tags={
        'group': 'bytes_rate',
        'title': fields.TagReference('interface', gettext_noop("RX bytes rate (%(interface)s)")),
        'description': gettext_noop("Throughput of received packets."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'bytes_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Bps',
    })
    tx_errors = fields.CounterField()
    tx_errors_rate = fields.RateField("system.status#reboots", "#tx_errors", tags={
        'group': 'errors_rate',
        'title': fields.TagReference('interface', gettext_noop("TX errors rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmission errors."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'errors_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Hz',
    })
    rx_errors = fields.CounterField()
    rx_errors_rate = fields.RateField("system.status#reboots", "#rx_errors", tags={
        'group': 'errors_rate',
        'title': fields.TagReference('interface', gettext_noop("RX errors rate (%(interface)s)")),
        'description': gettext_noop("Rate of receive errors."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'errors_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Hz',
    })
    tx_drops = fields.CounterField()
    tx_drops_rate = fields.RateField("system.status#reboots", "#tx_drops", tags={
        'group': 'drops_rate',
        'title': fields.TagReference('interface', gettext_noop("TX drops rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmission drops."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'drops_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Hz',
    })
    rx_drops = fields.CounterField()
    rx_drops_rate = fields.RateField("system.status#reboots", "#rx_drops", tags={
        'group': 'drops_rate',
        'title': fields.TagReference('interface', gettext_noop("RX drops rate (%(interface)s)")),
        'description': gettext_noop("Rate of receive drops."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {
                'group': 'drops_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'Hz',
    })
    mtu = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("MTU (%(interface)s)")),
        'description': gettext_noop("Interface MTU (Maximum Transmission Unit)."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
        'unit': 'B',
    })

pool.register(models.InterfaceMonitor, InterfaceMonitorStreams)


class WifiInterfaceMonitorStreams(InterfaceMonitorStreams):
    channel = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Channel (%(interface)s)")),
        'description': gettext_noop("Channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        },
    })
    channel_width = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Channel width (%(interface)s)")),
        'description': gettext_noop("Width of the channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
        'unit': 'MHz',
    })
    bitrate = fields.FloatField(tags={
        'title': fields.TagReference('interface', gettext_noop("Bitrate (%(interface)s)")),
        'description': gettext_noop("Wireless radio bitrate."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
        'unit': 'Mbps',
    })
    rts_threshold = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RTS threshold (%(interface)s)")),
        'description': gettext_noop("RTS threshold."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
        'unit': 'B',
    })
    frag_threshold = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Fragmentation threshold (%(interface)s)")),
        'description': gettext_noop("Fragmentation threshold."),
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        },
        'unit': 'B',
    })
    signal = fields.IntegerField(tags={
        'group': 'signal_noise',
        'title': fields.TagReference('interface', gettext_noop("Signal (%(interface)s)")),
        'description': gettext_noop("Amount of signal."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'signal_noise',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'dBm',
    })
    noise = fields.IntegerField(tags={
        'group': 'signal_noise',
        'title': fields.TagReference('interface', gettext_noop("Noise (%(interface)s)")),
        'description': gettext_noop("Amount of noise."),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'signal_noise',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'dBm',
    })
    snr = fields.FloatField(tags={
        'group': 'signal_noise',
        'title': fields.TagReference('interface', gettext_noop("Signal-to-noise ratio (%(interface)s)")),
        'description': gettext_noop("Signal-to-noise ratio."),
        'visualization': {
            'type': 'line',
            # We want signal-to-noise in graphs, but we hide it by the default to emphasise visualization on signal and noise.
            'initial_set': True,
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'signal_noise',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        },
        'unit': 'dBm',
    })

pool.register(models.WifiInterfaceMonitor, WifiInterfaceMonitorStreams)
