from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import components

from . import resources


api_urls.v1_api.register(resources.BabelTopologyLinkResource())


components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='olsr',
    weight=110,
    template='nodes/babel.html',
))
