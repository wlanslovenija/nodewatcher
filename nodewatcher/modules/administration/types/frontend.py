from nodewatcher.core.frontend import components


components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='type',
    template='display/type.html',
    extra_context=lambda context: {
        'node_type': context['node'].config.core.type(),
    }
))

components.partials.get_partial('network_topology_partial').add(components.PartialEntry(
    name='types',
    template='topology/types.html',
))

components.partials.get_partial('map_partial').add(components.PartialEntry(
    name='types',
    template='map/types.html',
))