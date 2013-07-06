from django.views.generic import list

from nodewatcher.core import models as core_models

class NodesList(list.ListView):
    template_name = 'nodes/list.html'
    queryset = core_models.Node.objects.regpoint("config").registry_fields(
        name = 'GeneralConfig.name',
        type = 'TypeConfig.type',
        router_id = 'RouterIdConfig.router_id',
        status = 'StatusMonitor.status',
    ).order_by('type', 'router_id')
