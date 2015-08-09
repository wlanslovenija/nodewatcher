from nodewatcher.core.frontend import components

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='location',
    weight=10,
    template='nodes/location.html',
    extra_context=lambda context: {
        'node_location': context['node'].config.core.location(),
    }
))

components.partials.get_partial('map_partial').add(components.PartialEntry(
    name='location',
    weight=-9000, # Ensure that this is the first entry
    template='location/map.html',
))
