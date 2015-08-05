from nodewatcher.core.frontend import components

# TODO: Should we make this conditional, so only in case the statistics module is loaded?
from nodewatcher.modules.frontend.statistics.pool import pool as statistics_pool

from . import resources


statistics_pool.register(resources.NodesByProjectResource())


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
