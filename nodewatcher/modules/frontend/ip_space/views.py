from django.views import generic
from django.db import models, migrations
from django.apps import apps

class IpSpace(generic.TemplateView):
    template_name = 'network/ip_space/ip_space.html'

    def get_context_data(self, **kwargs):
        IpPool = apps.get_model('core', 'IpPool')

        context = super(IpSpace, self).get_context_data(**kwargs)
        context['pools'] = IpPool.objects.all()
        return context
