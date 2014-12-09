from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool


class FirmwareVersionChanged(events.NodeEventRecord):
    """
    Node firmware version has been changed.
    """

    description = _("Firmware version has been changed from '%(old_version)s' to '%(new_version)s'.")

    def __init__(self, node, old_version, new_version):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param old_version: Old firmware version
        :param new_version: New firmware version
        """

        super(FirmwareVersionChanged, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_INFO,
            old_version=old_version,
            new_version=new_version,
        )

pool.register_record(FirmwareVersionChanged)
