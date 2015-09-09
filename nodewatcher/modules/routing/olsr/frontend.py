from nodewatcher.core.frontend import api, components

from . import resources


api.v1_api.register(resources.OlsrTopologyLinkResource())


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
