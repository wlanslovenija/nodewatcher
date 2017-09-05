from django.views import generic
from nodewatcher.core.allocation.ip.models import IpPool


class IpSpace(generic.TemplateView):
    template_name = 'network/ip_space/ip_space.html'

    def get_context_data(self, **kwargs):
        context = super(IpSpace, self).get_context_data(**kwargs)
        context['pools'] = IpPool.objects.all()
        return context
