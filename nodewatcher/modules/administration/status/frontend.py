from nodewatcher.core.frontend import components

# TODO: Should we make this conditional, so only in case the statistics module is loaded?
from nodewatcher.modules.frontend.statistics.pool import pool as statistics_pool

from . import models, resources


statistics_pool.register(resources.NodesByStatusResource())


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
