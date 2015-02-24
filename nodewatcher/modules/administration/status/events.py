from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool

# Need models to ensure that node.monitoring registration point is available
from . import models


class NodeStatusChange(events.NodeEventRecord):
    """
    Node status change event.
    """

    old_status = events.ChoiceAttribute('node.monitoring', 'core.status#network')
    new_status = events.ChoiceAttribute('node.monitoring', 'core.status#network')

    TRANSITIONS = {
        ('up', 'down'): (events.NodeEventRecord.SEVERITY_WARNING, _("Node has gone down.")),
        ('up', 'visible'): (None, None),
        ('down', 'up'): (events.NodeEventRecord.SEVERITY_INFO, _("Node has come up.")),
        ('down', 'visible'): (events.NodeEventRecord.SEVERITY_INFO, _("Node is now visible.")),
        ('visible', 'up'): (None, None),
        ('visible', 'down'): (events.NodeEventRecord.SEVERITY_WARNING, _("Node is no longer visible.")),
        (None, 'up'): (events.NodeEventRecord.SEVERITY_INFO, _("Node has come up.")),
        (None, 'visible'): (events.NodeEventRecord.SEVERITY_INFO, _("Node is now visible.")),
        (None, 'down'): (None, None),
    }

    def __init__(self, node, old_status, new_status):
        """
        Class constructor.

        :param node: Node that changed status
        :param old_status: Previous node status
        :param new_status: New node status
        """

        severity = self.TRANSITIONS.get((old_status, new_status), (None,))[0]
        if severity is None:
            severity = events.NodeEventRecord.SEVERITY_WARNING

        super(NodeStatusChange, self).__init__(
            node,
            severity,
            old_status=old_status,
            new_status=new_status
        )

    @classmethod
    def get_description(cls, data):
        return cls.TRANSITIONS.get(
            (data['old_status'], data['new_status']),
            (None, _("Node has changed status."))
        )[1]

    def post(self):
        """
        Posts this event.
        """

        # Ignore certain transitions.
        if self.TRANSITIONS.get((self.old_status, self.new_status), (None, None)) == (None, None):
            return

        super(NodeStatusChange, self).post()

pool.register_record(NodeStatusChange)
