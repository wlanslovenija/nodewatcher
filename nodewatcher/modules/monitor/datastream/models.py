from django_datastream import datastream

from nodewatcher.core.registry import registration

# To create node.monitoring registration point
import nodewatcher.core.monitor
from nodewatcher.core.monitor import models

from . import connect, fields


class MonitorRegistryItemMixin(object):
    """
    A mixin for all monitoring-related registry items that adds datastream
    special methods to each item.
    """

    def get_metric_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A list of tags that uniquely identify this object
        """

        return [
            {'node': self.root.uuid},
            {'registry_id': self.RegistryMeta.registry_id}
        ]

    def get_metric_tags(self):
        """
        Returns the metric tags that should be included in every metric
        derived from this object.

        :return: A list of tags to include
        """

        return [
            {'node': self.root.uuid},
            {'registry_id': self.RegistryMeta.registry_id}
        ]

    def get_metric_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all metrics derived from this object.
        """

        return datastream.Granularity.Minutes

# Adds datastream mixin to monitoring registration point
registration.point('node.monitoring').add_mixins(MonitorRegistryItemMixin)

# Adds mappings between monitoring registry items attributes and datastream fields
models.SystemStatusMonitor.connect_datastream = connect.ConnectDatastream(
    uptime=fields.IntegerField()
)
models.GeneralResourcesMonitor.connect_datastream = connect.ConnectDatastream(
    loadavg_1min=fields.FloatField(),
    loadavg_5min=fields.FloatField(),
    loadavg_15min=fields.FloatField(),
    memory_free=fields.IntegerField(),
    memory_buffers=fields.IntegerField(),
    memory_cache=fields.IntegerField(),
    processes=fields.IntegerField()
)
models.NetworkResourcesMonitor.connect_datastream = connect.ConnectDatastream(
    routes=fields.IntegerField(),
    tcp_connections=fields.IntegerField(),
    udp_connections=fields.IntegerField()
)
