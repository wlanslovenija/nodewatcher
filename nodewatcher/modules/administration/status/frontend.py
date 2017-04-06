from nodewatcher.core.frontend import components
from nodewatcher.core.api import urls as api_urls

from . import models, views

api_urls.v2_api.register('statistics/status', views.StatusStatisticsViewSet, base_name='statistics-status')

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='status',
    template='display/status.html',
    extra_context=lambda context: {
        'node_status': context['node'].monitoring.core.status(default=models.StatusMonitor),
    },
))

components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='status',
    template='network/statistics/status.html',
))
