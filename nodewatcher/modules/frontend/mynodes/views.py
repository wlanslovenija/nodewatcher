from django.views import generic

from nodewatcher.extra.accounts import mixins


class MyNodesList(mixins.AuthenticatedRequiredMixin, generic.TemplateView):
    template_name = 'nodes/mynodes.html'
