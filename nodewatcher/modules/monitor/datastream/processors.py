from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors

class Datastream(monitor_processors.NodeProcessor):
    """
    A processor that stores all monitoring data into the datastream.
    """
    def process(self, context, node):
        """
        Called for every processed node.

        @param context: Current context
        @param node: Node that is being processed
        @return: A (possibly) modified context
        """
        # TODO Should we enable addition of items that are not in the registry?
        for item in node.monitoring:
            # If the monitoring registry item doesn't provide a connect_datastream attribute,
            # we skip it as we don't know which fields to include
            if getattr(item, "connect_datastream", None) is None:
                continue

            item.connect_datastream.insert_to_stream(item, datastream)
