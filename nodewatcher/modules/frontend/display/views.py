from django.views import generic

from nodewatcher.core import models
from nodewatcher.core.frontend import views


class DisplayNode(views.NodeNameMixin, generic.DetailView):
    template_name = 'nodes/display.html'
    context_object_name = 'node'
    model = models.Node
