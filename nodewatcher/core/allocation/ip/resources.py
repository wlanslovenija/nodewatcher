from nodewatcher.core import resources as core_resources
from nodewatcher.core.registry import registration
from nodewatcher.core.frontend import api
from nodewatcher.core.frontend.api import fields as api_fields
# TODO: Remove this dependency after we have https://dev.wlan-si.net/ticket/1268.
from nodewatcher.modules.frontend.list import resources

from . import models as ip_models


# TODO: This is an ugly hack. There should be only one Node resource. See https://dev.wlan-si.net/ticket/1268.
class NodeResource(resources.NodeResource):
    class Meta(resources.NodeResource.Meta):
        fields = ('uuid', 'name')

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # We fake it here and set it to the same as registered resource.
        # It is not set because we have not registered this node resource.
        self._meta.urlconf_namespace = resources.NodeResource._meta.urlconf_namespace
        return super(NodeResource, self)._build_reverse_url(name, args=args, kwargs=kwargs)


class IpPoolResource(api.BaseResource):

    class Meta:
        queryset = ip_models.IpPool.objects.all().order_by('pk')
        resource_name = 'ip_pool'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        ordering = ('pk', 'family', 'network', 'status')


class NodeIpAllocationResource(core_resources.NodeSubresourceMixin, api.BaseResource):

    pool = api_fields.ToOneField(IpPoolResource, 'top_level', full=True)

    class Meta:
        resource_name = 'ip_allocations'
        queryset = ip_models.IpPool.objects.all().order_by('id')
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        ordering = ('id', 'family', 'network', 'status', 'pool')
        include_resource_uri = False

    def get_object_list(self, request):
        """
        Generate a list of all IP allocations for the current node.
        """

        allocations = None
        if hasattr(request, '_filter_node'):
            node = request._filter_node
            del request._filter_node

            allocation_sources = [
                item for item in registration.point('node.config').config_items() if issubclass(item, ip_models.IpAddressAllocator)
            ]

            allocations = []
            for src in allocation_sources:
                allocations += src.objects.filter(root=node).values_list('allocation__pk', flat=True)

        objects = super(NodeIpAllocationResource, self).get_object_list(request)
        if allocations is not None:
            return objects.filter(pk__in=allocations)
        else:
            return objects
