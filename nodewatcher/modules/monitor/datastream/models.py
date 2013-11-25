from django_datastream import datastream

from nodewatcher.core.registry import registration

# To create node.monitoring registration point
import nodewatcher.core.monitor
from nodewatcher.core.monitor import models

from . import connect, fields


class RegistryItemDatastreamAttributes(object):
    """
    Base class for registry item datastream attributes.
    """

    def __init__(self, obj):
        """
        Class constructor.

        :param obj: Model object
        """

        self.obj = obj

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A list of tags that uniquely identify this object
        """

        return [
            {'node': self.obj.root.uuid},
            {'registry_id': self.obj.RegistryMeta.registry_id}
        ]

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A list of tags to include
        """

        return [
            {'node': self.obj.root.uuid},
            {'registry_id': self.obj.RegistryMeta.registry_id}
        ]

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes

# Adds mappings between monitoring registry items attributes and datastream fields
models.SystemStatusMonitor.connect_datastream = connect.ConnectDatastream(
    RegistryItemDatastreamAttributes,
    uptime=fields.IntegerField(),
    reboots=fields.ResetField("#uptime"),
)

models.GeneralResourcesMonitor.connect_datastream = connect.ConnectDatastream(
    RegistryItemDatastreamAttributes,
    loadavg_1min=fields.FloatField(),
    loadavg_5min=fields.FloatField(),
    loadavg_15min=fields.FloatField(),
    memory_free=fields.IntegerField(),
    memory_buffers=fields.IntegerField(),
    memory_cache=fields.IntegerField(),
    processes=fields.IntegerField()
)

models.NetworkResourcesMonitor.connect_datastream = connect.ConnectDatastream(
    RegistryItemDatastreamAttributes,
    routes=fields.IntegerField(),
    tcp_connections=fields.IntegerField(),
    udp_connections=fields.IntegerField()
)

class InterfaceDatastreamAttributes(RegistryItemDatastreamAttributes):

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A list of tags that uniquely identify this object
        """

        return super(InterfaceDatastreamAttributes, self).get_stream_query_tags() + [
            {'interface': self.obj.name}
        ]

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A list of tags to include
        """

        return super(InterfaceDatastreamAttributes, self).get_stream_tags() + [
            {'interface': self.obj.name}
        ]

models.InterfaceMonitor.connect_datastream = connect.ConnectDatastream(
    InterfaceDatastreamAttributes,
    tx_packets=fields.IntegerField(),
    tx_packets_rate=fields.RateField("system.status#reboots", "#tx_packets"),
    rx_packets=fields.IntegerField(),
    rx_packets_rate=fields.RateField("system.status#reboots", "#rx_packets"),
    tx_bytes=fields.IntegerField(),
    tx_bytes_rate=fields.RateField("system.status#reboots", "#tx_bytes"),
    rx_bytes=fields.IntegerField(),
    rx_bytes_rate=fields.RateField("system.status#reboots", "#rx_bytes"),
    tx_errors=fields.IntegerField(),
    tx_errors_rate=fields.RateField("system.status#reboots", "#tx_errors"),
    rx_errors=fields.IntegerField(),
    rx_errors_rate=fields.RateField("system.status#reboots", "#rx_errors"),
    tx_drops=fields.IntegerField(),
    tx_drops_rate=fields.RateField("system.status#reboots", "#tx_drops"),
    rx_drops=fields.IntegerField(),
    rx_drops_rate=fields.RateField("system.status#reboots", "#rx_drops"),
    mtu=fields.IntegerField()
)

models.WifiInterfaceMonitor.connect_datastream = connect.ConnectDatastream(
    InterfaceDatastreamAttributes,
    channel=fields.IntegerField(),
    channel_width=fields.IntegerField(),
    bitrate=fields.FloatField(),
    rts_threshold=fields.IntegerField(),
    frag_threshold=fields.IntegerField(),
    signal=fields.IntegerField(),
    noise=fields.IntegerField(),
    snr=fields.FloatField()
)
