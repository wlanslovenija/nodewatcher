from nodewatcher.core.api import serializers as api_serializers, urls as api_urls
from nodewatcher.core.frontend import components

from . import serializers, views

api_serializers.pool.register(serializers.IpPoolSerializer)
api_urls.v2_api.register('pool/ip', views.IpPoolViewSet)

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='ip_allocations',
    weight=90,
    template='nodes/ip_allocations.html',
))
