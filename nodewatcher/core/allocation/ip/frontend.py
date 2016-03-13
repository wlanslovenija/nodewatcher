from nodewatcher.core.api import urls
from nodewatcher.core.frontend import components

from . import resources


urls.v1_api.register(resources.IpPoolResource())
urls.v1_api.register(resources.NodeIpAllocationResource())


components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='ip_allocations',
    weight=90,
    template='nodes/ip_allocations.html',
))
