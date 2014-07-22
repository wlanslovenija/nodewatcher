from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='location',
    template='nodes/snippet/location.html',
    extra_context=lambda context: {
        'node_location': context['node'].config.core.location(),
    }
))
