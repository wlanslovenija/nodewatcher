from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='project',
    template='nodes/snippet/project.html',
    extra_context=lambda context: {
        'node_project': getattr(context['node'].config.core.project(), 'project', None),
    }
))
