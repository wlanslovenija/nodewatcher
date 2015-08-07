from nodewatcher.core.frontend import components


components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='type',
    template='nodes/types/type.html',
    extra_context=lambda context: {
        'node_type': context['node'].config.core.type(),
    }
))

components.partials.get_partial('network_topology_partial').add(components.PartialEntry(
    name='types',
    template='types/topology.html',
))
