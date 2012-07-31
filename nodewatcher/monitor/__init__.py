from nodewatcher.registry import registration

class MonitorRegistryItemMixin(object):
  """
  A mixin for all monitoring-related registry items that adds datastream
  special methods to each item.
  """
  def get_metric_id(self, name):
    """
    Generates a unique metric identifier.

    :param name: Metric name
    :return: A unique metric identifier for this registry item and metric name
    """
    return "%s/%s/%s" % (self.root.get_object_id(), self.RegistryMeta.registry_id, name)

  def get_metric_tags(self):
    """
    Returns the metric tags that should be included in every metric
    derived from this object.
    """
    return dict(node = self.root.uuid)

# Create registration point
registration.create_point("nodes.Node", "monitoring", mixins = [MonitorRegistryItemMixin])

