from django.utils.translation import ugettext_lazy as _


class NodeNameMixin(object):
    def get_context_data(self, **kwargs):
        context = super(NodeNameMixin, self).get_context_data(**kwargs)
        context['node_name'] = self.object.config.core.general().name or _("unknown")
        return context
