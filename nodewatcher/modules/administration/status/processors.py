import datetime

from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors

from . import models, events


class NodeStatus(monitor_processors.NodeProcessor):
    """
    A processor that determines the node's status based on the status of
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
        prev_network = sm.network
        if context.node_available is not True:
            sm.network = 'down'
            sm.monitored = None
        else:
            # At least one of the processors must signal node reachability; these signals
            # can be produced by OLSR/HTTP telemetry/RTT processors
            if context.node_responds is True or context.http.successfully_parsed is True:
                sm.network = 'up'
                if context.http.successfully_parsed is True:
                    sm.monitored = True
                else:
                    sm.monitored = False
            else:
                sm.network = 'visible'
                if context.http.successfully_parsed is False:
                    # HTTP fetch was tried, but failed
                    sm.monitored = False
                else:
                    assert context.http.successfully_parsed is not True
                    # HTTP fetch was not tried so we don't know whether the node is monitored
                    sm.monitored = None
        # TODO: Change depending on any warning/error events
        sm.health = None
        sm.save()

        # Emit event on node state transitions
        if prev_network != sm.network:
            events.NodeStatusChange(node, prev_network, sm.network).post()

        return context


class PushNodeStatus(monitor_processors.NetworkProcessor):
    """
    A processor which updates status for nodes that push data.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        # Get all push nodes which should be down.
        down_nodes = core_models.Node.objects.regpoint('config').registry_fields(
            source='core.telemetry.http#source'
        ).regpoint('monitoring').registry_fields(
            last_seen='core.general#last_seen',
            network_status='core.status#network',
        ).filter(
            source='push',
            last_seen__lt=timezone.now() - datetime.timedelta(minutes=30),
            network_status='up',
        )

        # Update node status.
        models.StatusMonitor.objects.filter(root__in=down_nodes).update(network='down')

        return context, nodes
