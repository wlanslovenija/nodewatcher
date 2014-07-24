from tastypie import fields

from nodewatcher.core.frontend import api
from nodewatcher.modules.frontend.list import resources

from . import models


# We create a new node resource which has only name field available (along with resource_uri)
class NodeResource(resources.NodeResource):
    class Meta(resources.NodeResource.Meta):
        fields = ('name',)

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # We fake it here and set it to the same as registered resource.
        # It is not set because we have not registered this node resource.
        self._meta.urlconf_namespace = resources.NodeResource._meta.urlconf_namespace
        return super(NodeResource, self)._build_reverse_url(name, args=args, kwargs=kwargs)


def related_nodes(bundle):
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

    related_nodes = fields.ManyToManyField(to=NodeResource, attribute=related_nodes, full=True, help_text=models.SerializedNodeEvent._meta.get_field('related_nodes').help_text)
