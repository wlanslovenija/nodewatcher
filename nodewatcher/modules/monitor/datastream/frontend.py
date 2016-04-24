import datetime

from django.utils import timezone

from tastypie import resources

from django_datastream import urls as datastream_urls

from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import components
from nodewatcher.core.registry import exceptions as registry_exceptions


def register_resource(resource):
    # We have to make a resource which is namespaced for resource_uri to be correctly generated.
    class Resource(resources.NamespacedModelMixin, resource.__class__):
        pass

    api_urls.v1_api.register(Resource())

for resource in datastream_urls.v1_api._registry.values():
    register_resource(resource)


def extra_context(context):
    # Get the node's local timezone using the location schema.
    try:
        # TODO: Should this go to some method on the node class?
        node_zone = context['node'].config.core.location().timezone or timezone.utc
    except (registry_exceptions.RegistryItemNotRegistered, AttributeError):
        node_zone = timezone.utc

    try:
        timezone_offset = node_zone.utcoffset(datetime.datetime.now(), is_dst=False)
    except TypeError:
        # Timezone does not have a is_dst keyword argument.
        timezone_offset = node_zone.dst(datetime.datetime.now())

    return {
        # Python and JavaScript timezone offsets are inverted.
        'timezone_offset': -int(timezone_offset.total_seconds() // 60)
    }


components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='graphs',
    template='nodes/display/graphs.html',
    weight=1000, # Graphs should be towards the end.
    extra_context=extra_context
))
