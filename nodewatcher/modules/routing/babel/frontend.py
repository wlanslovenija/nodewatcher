from nodewatcher.core.frontend import api, components

from . import resources


api.v1_api.register(resources.BabelTopologyLinkResource())


components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='olsr',
    weight=110,
    template='nodes/babel.html',
))
