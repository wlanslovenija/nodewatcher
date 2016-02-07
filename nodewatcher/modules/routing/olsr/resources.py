from django.db import models as django_models

from nodewatcher.core import models as core_models, resources as core_resources
from nodewatcher.core.frontend import api
from nodewatcher.core.frontend.api import fields as api_fields
# TODO: Remove this dependency after we have https://dev.wlan-si.net/ticket/1268.
from nodewatcher.modules.frontend.list import resources

from . import models as olsr_models


# TODO: This is an ugly hack. There should be only one Node resource. See https://dev.wlan-si.net/ticket/1268.
class NodeResource(resources.NodeResource):
    class Meta(resources.NodeResource.Meta):
        fields = ('uuid', 'name', 'router_id')

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # We fake it here and set it to the same as registered resource.
        # It is not set because we have not registered this node resource.
        self._meta.urlconf_namespace = resources.NodeResource._meta.urlconf_namespace
        return super(NodeResource, self)._build_reverse_url(name, args=args, kwargs=kwargs)


class OlsrTopologyLinkResource(core_resources.NodeSubresourceMixin, api.BaseResource):

    peer = api_fields.ToOneField(NodeResource, 'peer', full=True)

    class Meta:
        resource_name = 'olsr_topology_link'
        node_filter = 'monitor__root'
        queryset = olsr_models.OlsrTopologyLink.objects.prefetch_related(
            django_models.Prefetch(
                'peer',
                queryset=core_models.Node.objects.regpoint('config').registry_fields(
                    name='core.general#name',
                    router_id='core.routerid',
                )
            ),
        ).order_by('id')
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        ordering = ('id', 'peer', 'lq', 'ilq', 'etx', 'last_seen')
        include_resource_uri = False
