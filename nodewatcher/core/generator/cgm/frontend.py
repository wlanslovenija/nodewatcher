from nodewatcher.core.frontend import components


components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='cgm',
    template='network/statistics/cgm.html',
    # TODO: Provide counts for each platform/router/version
    extra_context=lambda context: {},
))
