from nodewatcher.core.monitor import processors as monitor_processors

from . import events


class RebootValidator(monitor_processors.NodeProcessor):
    """
    Stores interface monitoring data.
    """

    def get_uptime(self, node):
        """
        Helper function for returning the current uptime.
        """

        status = node.monitoring.system.status()
        if status is not None:
            return status.uptime

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        self.old_uptime = self.get_uptime(node)

        return context

    def cleanup(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        """

        new_uptime = self.get_uptime(node)
        if new_uptime < self.old_uptime:
            events.NodeRebooted(node, self.old_uptime, new_uptime).post()
