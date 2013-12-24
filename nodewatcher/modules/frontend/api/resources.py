from tastypie import resources

from django_datastream import serializers

from nodewatcher.core import models


class NodeResource(resources.NamespacedModelResource):
    class Meta:
        queryset = models.Node.objects.all()
        resource_name = 'node'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        serializer = serializers.DatastreamSerializer()
