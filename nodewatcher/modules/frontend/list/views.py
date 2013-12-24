from django.views import generic

from nodewatcher.core import models as core_models


class NodesList(generic.ListView):
    template_name = 'nodes/list.html'
    queryset = core_models.Node.objects.regpoint('config').registry_fields(
        name='GeneralConfig.name',
        type='TypeConfig.type',
        router_id='RouterIdConfig.router_id',
        network_status='StatusMonitor.network',
        monitored_status='StatusMonitor.monitored',
        health_status='StatusMonitor.health',
    ).order_by('type', 'router_id')
    context_object_name = 'nodes'
