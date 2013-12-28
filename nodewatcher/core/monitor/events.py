from django.utils.translation import ugettext as _

from ..events import events

# Need models to ensure that node.monitoring registration point is available
from . import models


class TopologyLinkEstablished(events.NodeEventRecord):
    """
    Topology link established event.
    """

    routing_protocol = events.ChoiceAttribute('node.config', 'core.interfaces#routing_protocol')

    def __init__(self, node_a, node_b, routing_protocol):
        """
        Class constructor.

        :param node_a: Node on one side of the link
        :param node_b: Node on the other side of the link
        :param routing_protocol: Routing protocol
        """

        super(TopologyLinkEstablished, self).__init__(
            [node_a, node_b],
            events.NodeEventRecord.SEVERITY_INFO,
            _("Link between two nodes has been established"),
            routing_protocol=routing_protocol,
        )
