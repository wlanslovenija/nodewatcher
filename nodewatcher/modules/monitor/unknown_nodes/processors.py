import uuid

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors

from . import models


class DiscoverUnknownNodes(monitor_processors.NetworkProcessor):
    """
    A processor that discovers unknown nodes when they push data.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        if not context.push.source:
            return context, nodes

        try:
            core_models.Node.objects.get(uuid=context.push.source)
        except core_models.Node.DoesNotExist:
            # If there is currently no such node, add an unknown node record.
            try:
                models.UnknownNode.objects.update_or_create(
                    uuid=str(uuid.UUID(context.push.source)),
                    defaults={
                        'ip_address': context.identity.ip_address or None,
                        'certificate': dict(context.identity.certificate or {}) or None,
                        'origin': models.UnknownNode.PUSH,
                    },
                )
            except ValueError:
                # Ignore invalid UUIDs.
                pass

        return context, nodes
