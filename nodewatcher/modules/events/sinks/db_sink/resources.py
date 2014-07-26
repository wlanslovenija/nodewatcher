from tastypie import fields

from nodewatcher.core.frontend import api
from nodewatcher.modules.frontend.list import resources

from . import models


# We create a new node resource which has only name field available (along with resource_uri)
class NodeResource(resources.NodeResource):
    class Meta(resources.NodeResource.Meta):
        fields = ('uuid', 'name')

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # We fake it here and set it to the same as registered resource.
        # It is not set because we have not registered this node resource.
        self._meta.urlconf_namespace = resources.NodeResource._meta.urlconf_namespace
        return super(NodeResource, self)._build_reverse_url(name, args=args, kwargs=kwargs)


# We need a function which is also a string. Function is used in dehydrating
# ManyToManyField, string is used in apply_sorting to create an order_by argument.
class RelatedNodes(str):
    def __call__(self, bundle):
        # Add name to related nodes
        return bundle.obj.related_nodes.regpoint('config').registry_fields(
            name='core.general#name',
        )


class EventResource(api.BaseResource):
    class Meta:
        queryset = models.SerializedNodeEvent.objects.all().order_by('-timestamp')
        resource_name = 'event'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        ordering = ('timestamp', 'related_nodes', 'title')
        global_filter = ('timestamp', 'related_nodes__config_core_generalconfig__name', 'title')

    # TODO: How can we generate order_by string from registry, without hardcoding config_core_generalconfig?
    related_nodes = fields.ManyToManyField(to=NodeResource, attribute=RelatedNodes('related_nodes__config_core_generalconfig__name'), full=True, help_text=models.SerializedNodeEvent._meta.get_field('related_nodes').help_text)
