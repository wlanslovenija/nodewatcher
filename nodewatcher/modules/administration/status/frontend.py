from nodewatcher.core.frontend import components

from . import models


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='status',
    template='nodes/snippet/status.html',
    extra_context=lambda context: {
        'node_status': context['node'].monitoring.core.status(default=models.StatusMonitor),
    },
))
