from django_datastream import datastream

from nodewatcher.registry import registration

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
          { "node" : self.root.uuid },
          { "registry_id" : self.RegistryMeta.registry_id }
        ]

    def get_metric_tags(self):
        """
        Returns the metric tags that should be included in every metric
        derived from this object.

        :return: A list of tags to include
        """
        return [
          { "node" : self.root.uuid },
          { "registry_id" : self.RegistryMeta.registry_id }
        ]

    def get_metric_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all metrics derived from this object.
        """
        return datastream.Granularity.Minutes

# Create registration point
registration.create_point("nodes.Node", "monitoring", mixins = [MonitorRegistryItemMixin])
