from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors


class Datastream(monitor_processors.NodeProcessor):
    """
    A processor that stores all monitoring data into the datastream.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # TODO: Should we enable addition of items that are not in the registry?
        for item in node.monitoring:
            # If the monitoring registry item doesn't provide a connect_datastream attribute,
            # we skip it as we don't know which fields to include
            if getattr(item, "connect_datastream", None) is None:
                continue

            item.connect_datastream.insert_to_stream(item.__class__, item, datastream)


class Maintenance(monitor_processors.NetworkProcessor):
    """
    Datastream maintenance processor.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        datastream.backprocess_streams()

        return context, nodes
