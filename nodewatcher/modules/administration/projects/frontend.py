from nodewatcher.core.frontend import components
from nodewatcher.core.api import serializers as api_serializers, urls as api_urls

from . import serializers, views

api_serializers.pool.register(serializers.ProjectSerializer)
api_urls.v2_api.register('project', views.ProjectViewSet)
api_urls.v2_api.register('statistics/project', views.ProjectStatisticsViewSet, base_name='statistics-project')

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='project',
    template='nodes/snippet/project.html',
    extra_context=lambda context: {
        'node_project': getattr(context['node'].config.core.project(), 'project', None),
    }
))

components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='project',
    template='network/statistics/project.html',
    weight=50,
))
