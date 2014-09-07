from nodewatcher.core.frontend import components


components.partials.get_partial('network_topology_partial').add(components.PartialEntry(
    name='olsr',
    template='olsr/topology.html',
))
