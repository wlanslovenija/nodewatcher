from django.utils.translation import ugettext as _

from nodewatcher.core.events import events

# Need models to ensure that node.monitoring registration point is available
from . import models


class NodeStatusChange(events.NodeEventRecord):
    """
    Node status change event.
    """

    old_status = events.ChoiceAttribute('node.monitoring', 'core.status#network')
    new_status = events.ChoiceAttribute('node.monitoring', 'core.status#network')

    TRANSITIONS = {
        ('up', 'down'): (events.NodeEventRecord.SEVERITY_WARNING, _("Node has gone down")),
        ('up', 'visible'): (events.NodeEventRecord.SEVERITY_WARNING, _("Node is no longer reachable")),
        ('down', 'up'): (events.NodeEventRecord.SEVERITY_INFO, _("Node has come up")),
        ('down', 'visible'): (events.NodeEventRecord.SEVERITY_INFO, _("Node is now visible")),
        ('visible', 'up'): (events.NodeEventRecord.SEVERITY_INFO, _("Node is now reachable")),
        ('visible', 'down'): (events.NodeEventRecord.SEVERITY_WARNING, _("Node is no longer visible")),
        ('unknown', 'up'): (events.NodeEventRecord.SEVERITY_INFO, _("Node has come up")),
        ('unknown', 'visible'): (events.NodeEventRecord.SEVERITY_INFO, _("Node is now visible")),
        ('unknown', 'down'): (None, None),
    }

    def __init__(self, node, old_status, new_status):
        """
        Class constructor.

        :param node: Node that changed status
        :param old_status: Previous node status
        :param new_status: New node status
        """

        severity, title = self.TRANSITIONS.get(
            (old_status, new_status),
            (events.NodeEventRecord.SEVERITY_WARNING, _("Node has changed status"))
        )

        super(NodeStatusChange, self).__init__(
            node,
            severity,
            title,
            old_status=old_status,
            new_status=new_status
        )

    def post(self):
        """
        Posts this event.
        """

        if not self.title:
            return

        super(NodeStatusChange, self).post()
