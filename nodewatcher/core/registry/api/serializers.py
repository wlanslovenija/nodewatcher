from django.db import models
from django.db.models import constants

from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers, exceptions as api_exceptions
from nodewatcher.core.registry import registration

from . import fields as api_fields
from .. import fields as model_fields

# Exports.
__all__ = [
    'RegisteredChoiceSerializer',
    'RegistryRootSerializerMixin',
    'RegistryItemSerializerMixin',
]


class RegisteredChoiceSerializer(serializers.Serializer):
    """
    Serializer for registered choices.
    """

    name = serializers.CharField()
    verbose_name = serializers.CharField()
    help_text = serializers.CharField()
    icon = serializers.CharField()

    def __init__(self, *args, **kwargs):
        """
        Construct registered choice serializer.
        """

        regpoint = kwargs.pop('regpoint', None)
        choices = kwargs.pop('choices', None)
        if not choices or not regpoint:
            raise ValueError("Registered choice serializer must specify 'regpoint' and 'choices' parameters!")

        self._choices = registration.point(regpoint).get_registered_choices(choices)

        super(RegisteredChoiceSerializer, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        """
        Resolve plain value into the correct registred choice instance.
        """

        value = super(RegisteredChoiceSerializer, self).get_attribute(instance)
        try:
            return self._choices.resolve(value).get_json()
        except KeyError:
            return None


class RegistryRootSerializerMixin(object):
    """
    Mixin for serializing registry roots.
    """

    def get_field_names(self, *args, **kwargs):
        fields = super(RegistryRootSerializerMixin, self).get_field_names(*args, **kwargs)

        # Exclude internal fields.
        fields.remove('registry_metadata')

        return fields

    def to_representation(self, instance):
        data = super(RegistryRootSerializerMixin, self).to_representation(instance)

        for field in instance._meta.virtual_fields:
            if not hasattr(field, 'src_model'):
                continue

            # Skip internal fields, which are added when ordering.
            if field.name.startswith('_order_field_'):
                continue

            def serialize_instance(item):
                if hasattr(field, '_registry_annotations'):
                    for target_attribute, source_attribute in field._registry_annotations.items():
                        setattr(item, target_attribute, getattr(instance, source_attribute))

                return item._registry.serializer_class(item).data

            meta = field.src_model._registry
            value = getattr(instance, field.name)
            namespace = data.setdefault(meta.registration_point.namespace, {})
            if field.src_field:
                atoms = field.src_field.split(constants.LOOKUP_SEP)
                if atoms[0] in meta.sensitive_fields:
                    continue

                if isinstance(value, models.Manager):
                    base_container = namespace.setdefault(meta.registry_id, [])
                    for index, item in enumerate(value.all()):
                        try:
                            container = base_container[index]
                        except IndexError:
                            container = {}
                            base_container.append(container)

                        container = reduce(lambda a, b: a.setdefault(b, {}), atoms[:-1], container)
                        container[atoms[-1]] = item
                        annotate_instance(meta, base_container[index])
                else:
                    base_container = namespace.setdefault(meta.registry_id, {})
                    container = reduce(lambda a, b: a.setdefault(b, {}), atoms[:-1], base_container)

                    if isinstance(value, models.Model):
                        try:
                            serializer = api_serializers.pool.get_serializer(value.__class__)
                        except api_exceptions.SerializerNotRegistered:
                            # Don't know how to serialize the model, construct a default serializer.
                            class meta_cls:
                                model = value.__class__

                            serializer = type('DefaultModelSerializer', (serializers.ModelSerializer,), {'Meta': meta_cls})

                        value = serializer(value).data

                    container[atoms[-1]] = value
                    annotate_instance(meta, base_container)
            elif isinstance(value, models.Manager):
                namespace[meta.registry_id] = map(serialize_instance, value.all())
            else:
                namespace[meta.registry_id] = serialize_instance(value)

        return data


class RegistryItemSerializerMixin(object):
    """
    Mixin for serializing registry items.
    """

    def get_field_names(self, *args, **kwargs):
        model = getattr(self.Meta, 'model')
        fields = super(RegistryItemSerializerMixin, self).get_field_names(*args, **kwargs)

        # Exclude internal fields.
        fields.remove('polymorphic_ctype')
        fields.remove('root')
        fields.remove('display_order')
        fields.remove('annotations')

        # Remove all sensitive fields.
        for field_name in model._registry.sensitive_fields:
            fields.remove(field_name)

        return fields

    def build_relational_field(self, field_name, relation_info):
        if isinstance(relation_info.model_field, model_fields.IntraRegistryForeignKey):
            return (api_fields.IntraRegistryForeignKeyField, {'related_model': relation_info.related_model})
        elif isinstance(relation_info.model_field, models.ForeignKey):
            return (api_fields.ForeignKeyField, {'related_model': relation_info.related_model})

        return super(RegistryItemSerializerMixin, self).build_relational_field(field_name, relation_info)

    def to_representation(self, instance):
        data = super(RegistryItemSerializerMixin, self).to_representation(instance)

        # Add JSON-LD annotations.
        annotate_instance(instance._registry, data, self)

        return data


def annotate_instance(meta, data, serializer=None):
    data['@context'] = {
        '@base': '_:%s' % meta.get_api_id(),
        # TODO: Also include @vocab.
    }

    if 'id' in data:
        data['@id'] = str(data['id'])
        del data['id']

    data['@type'] = meta.get_api_type()
