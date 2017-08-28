from django import dispatch
from django.db.models import signals as django_signals

from nodewatcher.core import models as core_models

from . import tasks


@dispatch.receiver(django_signals.post_delete, sender=core_models.Node)
def datastream_node_removed(sender, instance, **kwargs):
    """
    Remove all streams when a node gets removed.
    """

    tasks.delete_streams.delay({'node': instance.pk})

# In case we have the frontend module installed, we also subscribe to its
# reset signal that gets called when a user requests a node's data to be reset
try:
    from nodewatcher.modules.frontend.editor import signals as editor_signals

    @dispatch.receiver(editor_signals.reset_node)
    def datastream_node_reset(sender, request, node, **kwargs):
        """
        Remove all streams when a user requests the node to be reset.
        """

        tasks.delete_streams.delay({'node': node.pk})
except ImportError:
    pass
