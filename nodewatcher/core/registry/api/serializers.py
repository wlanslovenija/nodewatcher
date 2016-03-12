from django.db import models

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

        # Rename 'registry_metadata' to just 'metadata'.
        data['metadata'] = data.pop('registry_metadata')

        for field in instance._meta.virtual_fields:
            if not hasattr(field, 'src_model'):
                continue

            meta = field.src_model._registry
            value = getattr(instance, field.name)
            namespace = data.setdefault(meta.registration_point.namespace, {})
            if field.src_field:
                if isinstance(value, models.Manager):
                    namespace.setdefault(meta.registry_id, {})[field.src_field] = value.all()
                else:
                    namespace.setdefault(meta.registry_id, {})[field.src_field] = value
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

        # Include type information as registry items are polymorphic.
        # TODO: Registry items should somehow declare what should go here instad of using the class name.
        data['type'] = instance.__class__.__name__.replace(instance._registry.registration_point.namespace.capitalize(), '')

        return data
