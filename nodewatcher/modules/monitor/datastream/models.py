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
            'registry_id': self._model.RegistryMeta.registry_id,
        }

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A dictionary of tags to include
        """

        return {
            'node': self._model.root.uuid,
            'registry_id': self._model.RegistryMeta.registry_id,
        }

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes


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
        'description': gettext_noop("Uptime of the node's system."),
        'visualization': {
            'type': 'line',
            'hidden': True,
        }
    })
    reboots = fields.ResetField("#uptime", tags={
        'visualization': {
            'type': 'event',
        }
    })

pool.register(models.SystemStatusMonitor, SystemStatusMonitorStreams)


class GeneralResourcesMonitorStreams(RegistryItemStreams):
    loadavg_1min = fields.FloatField(tags={
        'group': 'load_average',
        'description': gettext_noop("1 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average'},
        }
    })
    loadavg_5min = fields.FloatField(tags={
        'group': 'load_average',
        'description': gettext_noop("5 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average'},
        }
    })
    loadavg_15min = fields.FloatField(tags={
        'group': 'load_average',
        'description': gettext_noop("15 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average'},
        }
    })
    memory_free = fields.IntegerField(tags={
        'group': 'memory',
        'description': gettext_noop("Amount of free memory."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory'},
        }
    })
    memory_buffers = fields.IntegerField(tags={
        'group': 'memory',
        'description': gettext_noop("Amount of memory used for kernel buffers."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory'},
        }
    })
    memory_cache = fields.IntegerField(tags={
        'group': 'memory',
        'description': gettext_noop("Amount of memory used for cache."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory'},
        }
    })
    processes = fields.IntegerField(tags={
        'description': gettext_noop("Number of running processes."),
        'visualization': {
            'type': 'line',
        }
    })

pool.register(models.GeneralResourcesMonitor, GeneralResourcesMonitorStreams)


class NetworkResourcesMonitorStreams(RegistryItemStreams):
    routes = fields.IntegerField(tags={
        'description': gettext_noop("Number of routes installed in the kernel routing tables."),
        'visualization': {
            'type': 'line',
        }
    })
    tcp_connections = fields.IntegerField(tags={
        'description': gettext_noop("Number of tracked TCP connections."),
        'visualization': {
            'type': 'line',
        }
    })
    udp_connections = fields.IntegerField(tags={
        'description': gettext_noop("Number of tracked UDP connections."),
        'visualization': {
            'type': 'line',
        }
    })


class InterfaceStreams(RegistryItemStreams):
    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        tags = super(InterfaceStreams, self).get_stream_query_tags()
        tags.update({'interface': self._model.name})
        return tags

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A dictionary of tags to include
        """

        tags = super(InterfaceStreams, self).get_stream_tags()
        tags.update({'interface': self._model.name})
        return tags


class InterfaceMonitorStreams(InterfaceStreams):
    tx_packets = fields.IntegerField(tags={
        'description': gettext_noop("Number of transmitted packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    tx_packets_rate = fields.RateField("system.status#reboots", "#tx_packets", tags={
        'group': 'packets_rate',
        'description': gettext_noop("Rate of transmitted packets."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'packets_rate', 'interface': fields.TagReference('interface')},
        }
    })
    rx_packets = fields.IntegerField(tags={
        'description': gettext_noop("Number of received packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    rx_packets_rate = fields.RateField("system.status#reboots", "#rx_packets", tags={
        'group': 'packets_rate',
        'description': gettext_noop("Rate of received packets."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'packets_rate', 'interface': fields.TagReference('interface')},
        }
    })
    tx_bytes = fields.IntegerField(tags={
        'description': gettext_noop("Size of transmitted packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    tx_bytes_rate = fields.RateField("system.status#reboots", "#tx_bytes", tags={
        'group': 'bytes_rate',
        'description': gettext_noop("Throughput of transmitted packets."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'bytes_rate', 'interface': fields.TagReference('interface')},
        }
    })
    rx_bytes = fields.IntegerField(tags={
        'description': gettext_noop("Size of received packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    rx_bytes_rate = fields.RateField("system.status#reboots", "#rx_bytes", tags={
        'group': 'bytes_rate',
        'description': gettext_noop("Throughput of received packets."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'bytes_rate', 'interface': fields.TagReference('interface')},
        }
    })
    tx_errors = fields.IntegerField(tags={
        'description': gettext_noop("Number of transmission errors."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    tx_errors_rate = fields.RateField("system.status#reboots", "#tx_errors", tags={
        'group': 'errors_rate',
        'description': gettext_noop("Rate of transmission errors."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'errors_rate', 'interface': fields.TagReference('interface')},
        }
    })
    rx_errors = fields.IntegerField(tags={
        'description': gettext_noop("Number of receive errors."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    rx_errors_rate = fields.RateField("system.status#reboots", "#rx_errors", tags={
        'group': 'errors_rate',
        'description': gettext_noop("Rate of receive errors."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'errors_rate', 'interface': fields.TagReference('interface')},
        }
    })
    tx_drops = fields.IntegerField(tags={
        'description': gettext_noop("Number of dropped packets when transmitting."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    tx_drops_rate = fields.RateField("system.status#reboots", "#tx_drops", tags={
        'group': 'drops_rate',
        'description': gettext_noop("Rate of transmission drops."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'drops_rate', 'interface': fields.TagReference('interface')},
        }
    })
    rx_drops = fields.IntegerField(tags={
        'description': gettext_noop("Number of dropped packets when receiving."),
        'visualization': {
            'hidden': True,
            'type': 'line',
        }
    })
    rx_drops_rate = fields.RateField("system.status#reboots", "#rx_drops", tags={
        'group': 'drops_rate',
        'description': gettext_noop("Rate of receive errors."),
        'visualization': {
            'type': 'line',
            'with': {'group': 'drops_rate', 'interface': fields.TagReference('interface')},
        }
    })
    mtu = fields.IntegerField(tags={
        'description': gettext_noop("Interface MTU (Maximum Transmission Unit)."),
        'visualization': {
            'type': 'line',
        }
    })

pool.register(models.InterfaceMonitor, InterfaceMonitorStreams)


class WifiInterfaceMonitorStreams(InterfaceMonitorStreams):
    channel = fields.IntegerField(tags={
        'description': gettext_noop("Channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
        }
    })
    channel_width = fields.IntegerField(tags={
        'description': gettext_noop("Width of the channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
        }
    })
    bitrate = fields.FloatField(tags={
        'description': gettext_noop("Wireless radio bitrate."),
        'visualization': {
            'type': 'line',
        }
    })
    rts_threshold = fields.IntegerField(tags={
        'description': gettext_noop("RTS threshold."),
        'visualization': {
            'type': 'line',
        }
    })
    frag_threshold = fields.IntegerField(tags={
        'description': gettext_noop("Fragmentation threshold."),
        'visualization': {
            'type': 'line',
        }
    })
    signal = fields.IntegerField(tags={
        'description': gettext_noop("Amount of signal in dBm."),
        'visualization': {
            'type': 'line',
        }
    })
    noise = fields.IntegerField(tags={
        'description': gettext_noop("Amount of noise in dBm."),
        'visualization': {
            'type': 'line',
        }
    })
    snr = fields.FloatField(tags={
        'description': gettext_noop("Signal-to-noise ratio."),
        'visualization': {
            'type': 'line',
        }
    })

pool.register(models.WifiInterfaceMonitor, WifiInterfaceMonitorStreams)
