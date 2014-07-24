import sys

from django.utils import six

from tastypie import fields as tastypie_fields, resources
from tastypie.contrib.gis import resources as gis_resources

from django_datastream import serializers

from ...registry import fields as registry_fields

from . import fields

# Exports
__all__ = [
    'BaseResource',
]


# Adapted from PEP 257
def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return the first paragraph as a single string:
    return '\n'.join(trimmed).split('\n\n')[0]


class BaseMetaclass(resources.ModelDeclarativeMetaclass):
    def __new__(cls, name, bases, attrs):
        # Make serializers.DatastreamSerializer default serializer
        if attrs.get('Meta') and not getattr(attrs['Meta'], 'serializer', None):
            attrs['Meta'].serializer = serializers.DatastreamSerializer()
        return super(BaseMetaclass, cls).__new__(cls, name, bases, attrs)


class BaseResource(six.with_metaclass(BaseMetaclass, resources.NamespacedModelResource, gis_resources.ModelResource)):
    # In class methods which are called from a metaclass we cannot use super() because BaseResource is not
    # yet defined then. We cannot call gis_resources.ModelResource.<method>() either, because then our current
    # cls is not given, but gis_resources.ModelResource is used instead. So we create a custom function where skip
    # the @classmethod decorator and access underlying unbound function stored in im_func instead. We have to use
    # gis_resources.ModelResource branch of inheritance because it does not do it by itself, but it is OK, because
    # we do not really care about namespaces when called from a metaclass.

    @classmethod
    def should_skip_field(cls, field):
        def parent_should_skip_field():
            return gis_resources.ModelResource.should_skip_field.im_func(cls, field)

        if isinstance(field, registry_fields.RegistryRelationField):
            return False

        return parent_should_skip_field()

    @classmethod
    def api_field_from_django_field(cls, field, default=tastypie_fields.CharField):
        def parent_api_field_from_django_field():
            return gis_resources.ModelResource.api_field_from_django_field.im_func(cls, field, default)

        if not isinstance(field, registry_fields.RegistryRelationField):
            field_class = parent_api_field_from_django_field()

            def create_field(**kwargs):
                f = field_class(**kwargs)
                f.model_field = field
                return f

            return create_field

        else:
            def create_field(**kwargs):
                class Resource(BaseResource):
                    class Meta:
                        object_class = field.rel.to
                        resource_name = '%s.%s' % (field.rel.to.__module__, field.rel.to.__name__)
                        list_allowed_methods = ('get',)
                        detail_allowed_methods = ('get',)
                        serializer = serializers.DatastreamSerializer()
                        excludes = ['id']
                        include_resource_uri = False

                f = fields.RegistryRelationField(Resource, **kwargs)
                f.model_field = field
                return f

            return create_field

    @classmethod
    def get_fields(cls, fields=None, excludes=None):
        # Registry stores additional fields in as virtual fields and we reuse Tastypie
        # code to parse them by temporary assigning them to local fields

        def parent_get_fields():
            return gis_resources.ModelResource.get_fields.im_func(cls, fields, excludes)

        final_fields = parent_get_fields()

        if not cls._meta.object_class:
            return final_fields

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

    def build_schema(self):
        data = super(BaseResource, self).build_schema()

        for field_name, field_object in self.fields.items():
            # We process ListField specially here (and not use field's
            # build_schema) so that Tastypie's ListField can be used
            if isinstance(field_object, tastypie_fields.ListField):
                if getattr(field_object, 'field', None):
                    data['fields'][field_name]['content'] = {}

                    field_type = field_object.field.__class__.__name__.lower()
                    if field_type.endswith('field'):
                        field_type = field_type[:-5]
                    data['fields'][field_name]['content']['type'] = field_type

                    if field_object.field.__doc__:
                        data['fields'][field_name]['content']['help_text'] = trim(field_object.field.__doc__)

            if hasattr(field_object, 'build_schema'):
                data['fields'][field_name].update(field_object.build_schema())

            if getattr(field_object, 'model_field', None):
                if getattr(field_object.model_field, 'choices'):
                    choices = field_object.model_field.choices

                    try:
                        # Try to get only keys
                        choices = zip(*choices)[0]
                    except (KeyError, IndexError):
                        # If not possible, leave it as it is
                        pass

                    data['fields'][field_name].update({
                        'choices': choices,
                    })

        return data
