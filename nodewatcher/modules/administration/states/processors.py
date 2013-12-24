from nodewatcher.core.monitor import processors as monitor_processors

from . import models


class NodeState(monitor_processors.NodeProcessor):
    """
    A processor that determines the node's state based on the status of
    other processors (OLSR, HTTP telemetry, ...).
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        sm = node.monitoring.core.status(create=models.StatusMonitor)
        # TODO: Emit events on node state transitions
        if context.node_available is not True:
            sm.network = 'down'
            sm.monitored = None
        elif context.http.successfully_parsed is True:
            sm.network = 'up'
            sm.monitored = True
        else:
            sm.network = 'visible'
            sm.monitored = False
        # TODO: Change depending on any warning/error events
        sm.health = 'unknown'
        sm.save()

        return context
