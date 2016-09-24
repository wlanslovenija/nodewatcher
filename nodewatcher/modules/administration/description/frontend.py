from nodewatcher.core.frontend import components

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='url',
    template='nodes/general/url.html',
    weight=85,
    extra_context=lambda context: {
        'description': context['node'].config.core.description()
    },
))
