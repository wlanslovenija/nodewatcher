from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool

# Need models to ensure that node.monitoring registration point is available
from . import models as monitor_models


class TopologyLinkEstablished(events.NodeEventRecord):
    """
    Topology link established event.
    """

    description = _("Link between two nodes has been established.")
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
            routing_protocol=routing_protocol,
        )

    def post(self):
        # Only post events if this is a new adjacency that we have never seen before.
        adjacency, created = monitor_models.AdjancencyHistory.objects.get_or_create(
            node_a=self.related_nodes[0],
            node_b=self.related_nodes[1],
            protocol=self.routing_protocol,
        )

        if created:
            super(TopologyLinkEstablished, self).post()

pool.register_record(TopologyLinkEstablished)


class TelemetryProcessingFailed(events.NodeWarningRecord):
    """
    Telemetry failure event.
    """

    description = _("Telemetry processing has failed.")
    # TODO: Should this be changed into a choice attribute?
    method = events.CharAttribute(primary_key=True)

    def __init__(self, node, method):
        """
        Class constructor.

        :param node: Node on which the telemetry processing failed
        :param method: Telemetry processing method
        """

        super(TelemetryProcessingFailed, self).__init__(
            [node],
            events.NodeWarningRecord.SEVERITY_ERROR,
            method=method,
        )

pool.register_record(TelemetryProcessingFailed)
