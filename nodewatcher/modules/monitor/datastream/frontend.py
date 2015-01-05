from tastypie import resources

from django_datastream import urls

from nodewatcher.core.frontend import api, components


def register_resource(resource):
    # We have to make a resource which is namespaced for resource_uri to be correctly generated.
    class Resource(resources.NamespacedModelMixin, resource.__class__):
        pass

    api.v1_api.register(Resource())

for resource in urls.v1_api._registry.values():
    register_resource(resource)


components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='graphs',
    template='nodes/display/graphs.html',
    weight=1000, # Graphs should be towards the end.
))
