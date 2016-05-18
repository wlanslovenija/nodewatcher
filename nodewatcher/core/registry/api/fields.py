from django.core import urlresolvers

from rest_framework import fields, relations

from nodewatcher.core.api import serializers as api_serializers, exceptions as api_exceptions


class IntraRegistryForeignKeyField(fields.Field):
    def __init__(self, *args, **kwargs):
        self.related_model = kwargs.pop('related_model')
        super(IntraRegistryForeignKeyField, self).__init__(*args, **kwargs)

    def get_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        return {
            '@id': '_:%s' % self.related_model._registry.get_api_id(value.pk),
        }


class ForeignKeyField(fields.Field):
    def __init__(self, *args, **kwargs):
        self.related_model = kwargs.pop('related_model')
        super(ForeignKeyField, self).__init__(*args, **kwargs)

    def get_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        try:
            serializer = api_serializers.pool.get_serializer(self.related_model)
            base_view = getattr(serializer.Meta, 'base_view', None)
            if base_view is not None:
                return {
                    '@id': '%s%s' % (urlresolvers.reverse(base_view), value.pk)
                }
        except api_exceptions.SerializerNotRegistered:
            pass

        return str(value.pk)
