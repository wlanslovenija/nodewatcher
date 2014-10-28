from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='location',
    template='nodes/snippet/location.html',
    extra_context=lambda context: {
        'node_location': context['node'].config.core.location(),
    }
))

components.partials.get_partial('map_partial').add(components.PartialEntry(
    name='location',
    template='location/map.html',
))
