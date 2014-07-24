from nodewatcher.core.frontend import components


components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='project',
    template='nodes/snippet/project.html',
    extra_context=lambda context: {
        'node_project': getattr(context['node'].config.core.project(), 'project', None),
    }
))


components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='project',
    template='network/statistics/project.html',
    # TODO: Provide counts for each project
    extra_context=lambda context: {},
))
