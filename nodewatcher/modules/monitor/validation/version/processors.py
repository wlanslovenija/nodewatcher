from nodewatcher.core.monitor import processors as monitor_processors

from . import events


class VersionValidator(monitor_processors.NodeProcessor):
    """
    Detects firmware version changes.
    """

    def get_firmware_version(self, node):
        """
        Helper function for returning the current firmware version.
        """

        general = node.monitoring.core.general()
        if general is not None:
            return general.firmware

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        self.old_version = self.get_firmware_version(node)

        return context

    def cleanup(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        """

        new_version = self.get_firmware_version(node)
        if new_version != self.old_version:
            events.FirmwareVersionChanged(node, self.old_version, new_version).post()
