from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool


class NodeRebooted(events.NodeEventRecord):
    """
    Node has been rebooted.
    """

    description = _("Node has been rebooted.")

    def __init__(self, node, old_uptime, new_uptime):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param old_uptime: Old node uptime
        :param new_uptime: New node uptime
        """

        super(NodeRebooted, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            old_uptime=old_uptime,
            new_uptime=new_uptime,
        )

pool.register_record(NodeRebooted)
