from nodewatcher.core.api import serializers as api_serializers
from nodewatcher.core.frontend import components

from . import serializers

api_serializers.pool.register(serializers.BabelTopologyLinkSerializer)

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='babel',
    weight=110,
    template='nodes/babel.html',
))
