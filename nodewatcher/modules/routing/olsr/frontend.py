from nodewatcher.core.api import serializers as api_serializers
from nodewatcher.core.frontend import components

from . import serializers

api_serializers.pool.register(serializers.OlsrTopologyLinkSerializer)

components.partials.get_partial('network_topology_partial').add(components.PartialEntry(
    name='olsr',
    template='olsr/topology.html',
))

components.partials.get_partial('map_partial').add(components.PartialEntry(
    name='olsr',
    template='olsr/map.html',
))

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='olsr',
    weight=100,
    template='nodes/olsr.html',
))
