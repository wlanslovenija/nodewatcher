from django.contrib import messages
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core import models
from nodewatcher.core.registry import permissions

from . import signals


permissions.register(models.Node, 'reset_node', "Can reset node")


@receiver(signals.remove_node)
def node_removed_message(sender, request, node, **kwargs):
    messages.add_message(request, messages.INFO, _("Node successfully removed."), fail_silently=True)


@receiver(signals.reset_node)
def node_reset_message(sender, request, node, **kwargs):
    messages.add_message(request, messages.INFO, _("Node successfully reset."), fail_silently=True)
