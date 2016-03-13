from django.db import models
from django.db.models import constants

from rest_framework import serializers

# Exports.
__all__ = [
    'RegistryRootSerializerMixin',
    'RegistryItemSerializerMixin',
]


class RegistryRootSerializerMixin(object):
    """
    Mixin for serializing registry roots.
    """

    def to_representation(self, instance):
        data = super(RegistryRootSerializerMixin, self).to_representation(instance)

        del data['registry_metadata']

        for field in instance._meta.virtual_fields:
            if not hasattr(field, 'src_model'):
                continue

            meta = field.src_model._registry
            value = getattr(instance, field.name)
            namespace = data.setdefault(meta.registration_point.namespace, {})
            if field.src_field:
                container = namespace.setdefault(meta.registry_id, {})
                atoms = field.src_field.split(constants.LOOKUP_SEP)
                container = reduce(lambda a, b: a.setdefault(b, {}), atoms[:-1], container)

                if isinstance(value, models.Manager):
                    container[atoms[-1]] = value.all()
                else:
                    container[atoms[-1]] = value
            elif isinstance(value, models.Manager):
                values = []
                for item in value.all():
                    values.append(item._registry.serializer_class(item).data)

                namespace[meta.registry_id] = values
            else:
                namespace[meta.registry_id] = value._registry.serializer_class(value).data

        return data


class RegistryItemSerializerMixin(object):
    """
    Mixin for serializing registry items.
    """

    def to_representation(self, instance):
        data = super(RegistryItemSerializerMixin, self).to_representation(instance)

        # Remove some internal fields.
        del data['polymorphic_ctype']
        del data['root']
        del data['display_order']
        del data['annotations']

        # Include type information as registry items are polymorphic.
        # TODO: Registry items should somehow declare what should go here instad of using the class name.
        # TODO: We might use JSON-LD way of storing the type information.
        data['@type'] = instance.__class__.__name__.replace(instance._registry.registration_point.namespace.capitalize(), '')

        return data
