from django.apps import apps

from nodewatcher.core.frontend import components

# Register API serializers.
from . import serializers

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='project',
    template='nodes/snippet/project.html',
    extra_context=lambda context: {
        'node_project': getattr(context['node'].config.core.project(), 'project', None),
    }
))


# Provide statistics only in case the nodewatcher.modules.frontend.statistics app is installed.
if apps.is_installed('nodewatcher.modules.frontend.statistics'):
    from nodewatcher.modules.frontend.statistics.pool import pool as statistics_pool
    from . import resources

    statistics_pool.register(resources.NodesByProjectResource())

    components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
        name='project',
        template='network/statistics/project.html',
        weight=50,
    ))
