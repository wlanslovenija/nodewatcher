from nodewatcher.core.frontend import components

from . import models


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='last_seen',
    template='nodes/snippet/last_seen.html',
    extra_context=lambda context: {
        'node_last_seen': context['node'].monitoring.core.general(default=models.GeneralMonitor).last_seen
    },
))
