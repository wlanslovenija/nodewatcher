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

        :return: A list of tags that uniquely identify this object
        """

        return [
            {'node': self._model.root.uuid},
            {'registry_id': self._model.RegistryMeta.registry_id}
        ]

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A list of tags to include
        """

        return [
            {'node': self._model.root.uuid},
            {'registry_id': self._model.RegistryMeta.registry_id}
        ]

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes


class SystemStatusMonitorStreams(RegistryItemStreams):
    uptime = fields.IntegerField()
    reboots = fields.ResetField("#uptime")

pool.register(models.SystemStatusMonitor, SystemStatusMonitorStreams)


class GeneralResourcesMonitorStreams(RegistryItemStreams):
    loadavg_1min = fields.FloatField()
    loadavg_5min = fields.FloatField()
    loadavg_15min = fields.FloatField()
    memory_free = fields.IntegerField()
    memory_buffers = fields.IntegerField()
    memory_cache = fields.IntegerField()
    processes = fields.IntegerField()

pool.register(models.GeneralResourcesMonitor, GeneralResourcesMonitorStreams)


class NetworkResourcesMonitorStreams(RegistryItemStreams):
    routes = fields.IntegerField()
    tcp_connections = fields.IntegerField()
    udp_connections = fields.IntegerField()


class InterfaceStreams(RegistryItemStreams):
    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A list of tags that uniquely identify this object
        """

        return super(InterfaceStreams, self).get_stream_query_tags() + [
            {'interface': self._model.name}
        ]

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A list of tags to include
        """

        return super(InterfaceStreams, self).get_stream_tags() + [
            {'interface': self._model.name}
        ]


class InterfaceMonitorStreams(InterfaceStreams):
    tx_packets = fields.IntegerField()
    tx_packets_rate = fields.RateField("system.status#reboots", "#tx_packets")
    rx_packets = fields.IntegerField()
    rx_packets_rate = fields.RateField("system.status#reboots", "#rx_packets")
    tx_bytes = fields.IntegerField()
    tx_bytes_rate = fields.RateField("system.status#reboots", "#tx_bytes")
    rx_bytes = fields.IntegerField()
    rx_bytes_rate = fields.RateField("system.status#reboots", "#rx_bytes")
    tx_errors = fields.IntegerField()
    tx_errors_rate = fields.RateField("system.status#reboots", "#tx_errors")
    rx_errors = fields.IntegerField()
    rx_errors_rate = fields.RateField("system.status#reboots", "#rx_errors")
    tx_drops = fields.IntegerField()
    tx_drops_rate = fields.RateField("system.status#reboots", "#tx_drops")
    rx_drops = fields.IntegerField()
    rx_drops_rate = fields.RateField("system.status#reboots", "#rx_drops")
    mtu = fields.IntegerField()

pool.register(models.InterfaceMonitor, InterfaceMonitorStreams)


class WifiInterfaceMonitorStreams(InterfaceMonitorStreams):
    channel = fields.IntegerField()
    channel_width = fields.IntegerField()
    bitrate = fields.FloatField()
    rts_threshold = fields.IntegerField()
    frag_threshold = fields.IntegerField()
    signal = fields.IntegerField()
    noise = fields.IntegerField()
    snr = fields.FloatField()

pool.register(models.WifiInterfaceMonitor, WifiInterfaceMonitorStreams)
