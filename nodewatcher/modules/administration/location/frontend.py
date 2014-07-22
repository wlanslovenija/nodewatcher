from nodewatcher.core.frontend import components
from django.utils.translation import ugettext_lazy as _


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='location',
    template='nodes/snippet/location.html',
    extra_context=lambda context: {
        'node_location': context['node'].config.core.location(),
    }
))
