from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='type',
    template='nodes/snippet/type.html',
    extra_context=lambda context: {
        'node_type': context['node'].config.core.type(),
    }
))

components.partials.get_partial('network_topology_partial').add(components.PartialEntry(
    name='types',
    template='types/topology.html',
))
