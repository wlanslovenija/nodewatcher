from nodewatcher.core.frontend import components

from . import models, serializers, views


components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='last_seen',
    template='nodes/last_seen.html',
    extra_context=lambda context: {
        'node_last_seen': context['node'].monitoring.core.general(default=models.GeneralMonitor).last_seen
    },
))
