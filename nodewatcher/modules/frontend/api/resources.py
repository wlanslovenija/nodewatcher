from tastypie import resources

from django_datastream import serializers

from nodewatcher.core import models


class NodeResource(resources.NamespacedModelResource):
    class Meta:
        queryset = models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
            type='core.type#type',
            router_id='core.routerid#router_id',
            project='core.project#project.name',
        ).regpoint('monitoring').registry_fields(
            last_seen='core.general#last_seen',
            network_status='core.status#network',
            monitored_status='core.status#monitored',
            health_status='core.status#health',
            peers='network.routing.topology#link_count',
        )
        resource_name = 'node'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        serializer = serializers.DatastreamSerializer()

    @classmethod
    def get_fields(cls, fields=None, excludes=None):
        # Registry stores additional fields in as virtual fields and we reuse Tastypie
        # code to parse them by temporary assigning them to local fields

        def parent_get_fields():
            # Cannot use super() because this is called from a metaclass and NodeResource is not yet defined
            # We cannot call resources.NamespacedModelResource.get_fields() either, because then our current
            # cls is not given, but resources.NamespacedModelResource is used instead
            # So we have to skip the @classmethod decorator and access underlying unbound function stored
            # in im_func instead
            return resources.NamespacedModelResource.get_fields.im_func(cls, fields, excludes)

        final_fields = parent_get_fields()

        meta_fields = cls._meta.object_class._meta.local_fields
        try:
            cls._meta.object_class._meta.local_fields = cls._meta.object_class._meta.virtual_fields
            if hasattr(cls._meta.object_class._meta, 'fields'):
                del cls._meta.object_class._meta.fields
            cls._meta.object_class._meta._fill_fields_cache()
            final_fields.update(parent_get_fields())
        finally:
            cls._meta.object_class._meta.local_fields = meta_fields
            if hasattr(cls._meta.object_class._meta, 'fields'):
                del cls._meta.object_class._meta.fields
            cls._meta.object_class._meta._fill_fields_cache()

        return final_fields
