from nodewatcher.monitor import processors as monitor_processors
from nodewatcher.datastream.stream import stream

class DataStreamProcessor(monitor_processors.NodeProcessor):
  """
  A processor that stores all monitoring data into the data stream.
  """
  def process(self, context, node):
    """
    Called for every processed node.

    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    for item in node.monitoring:
      # If the monitoring registry item doesn't provide a data_stream attribute in
      # RegistryMeta, we skip it as we don't know which fields to include
      if getattr(item.RegistryMeta, "data_stream", None) is None:
        continue

      # Attempt to add every item into the data stream
      for field_name in item.RegistryMeta.data_stream:
        try:
          field_name, alias = field_name
          value = getattr(item, alias)
        except ValueError:
          value = getattr(item, field_name)

        # Push data into the data stream
        stream.insert(node, "%s.%s" % (item.RegistryMeta.registry_id, field_name), value)
