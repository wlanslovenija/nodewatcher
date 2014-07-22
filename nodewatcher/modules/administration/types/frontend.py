from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='type',
    template='nodes/snippet/type.html',
    extra_context=lambda context: {
        'node_type': context['node'].config.core.type(),
    }
))
