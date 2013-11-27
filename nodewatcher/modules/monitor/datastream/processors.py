from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors

from . import exceptions
from .pool import pool


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
            # Only include models that have known stream descriptors registered in
            # the descriptor pool
            try:
                descriptor = pool.get_descriptor(item)
                descriptor.insert_to_stream(datastream)
            except exceptions.StreamDescriptorNotRegistered:
                continue


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
