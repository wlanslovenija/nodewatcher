import sys

from django.contrib.gis.db import models as gis_models
from django.db.models import query
from django.utils import six

from tastypie import fields as tastypie_fields, resources
from tastypie.contrib.gis import resources as gis_resources

from django_datastream import serializers

import json_field

from ...registry import fields as registry_fields

from . import fields, paginator

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
        # Override Meta defaults
        if attrs.get('Meta') and not getattr(attrs['Meta'], 'serializer', None):
            attrs['Meta'].serializer = serializers.DatastreamSerializer()
        if attrs.get('Meta') and not getattr(attrs['Meta'], 'paginator_class', None):
            attrs['Meta'].paginator_class = paginator.Paginator
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

        # Skip fields created by the registry queryset internally for sorting purposes.
        if field.name.startswith('_'):
            return True

        if isinstance(field, registry_fields.RegistryRelationField):
            return False

        return parent_should_skip_field()

    @classmethod
    def api_field_from_django_field(cls, field, default=tastypie_fields.CharField):
        def parent_api_field_from_django_field():
            return gis_resources.ModelResource.api_field_from_django_field.im_func(cls, field, default)

        if not isinstance(field, registry_fields.RegistryRelationField):
            if isinstance(field, json_field.JSONField):
                # TODO: Optimize this so that double conversion is not performed and that we pass raw JSON.
                field_class = tastypie_fields.DictField
            elif isinstance(field, gis_models.GeometryField):
                # Override with our GeometryField that knows how to extract GeoJSON from
                # the queryset in order to avoid slow GDAL conversions.
                field_class = fields.GeometryField
            else:
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

    # A hook so that queryset can be further sorted after basic sorting has been
    # applied. This allows us to assure that there is always a defined order for
    # all objects even if basic sorting does not sort all objects (for example,
    # because key to sort on is the same for multiple objects). This is necessary
    # for pagination to work correctly, because SKIP and LIMIT works well for
    # pagination only when all objects have a defined order.
    def _after_apply_sorting(self, obj_list, options, order_by_args):
        return obj_list

    def apply_sorting(self, obj_list, options=None):
        # Makes sure sorting does not loose count of all objects before filtering.
        nonfiltered_count = obj_list._nonfiltered_count

        # To be able to assign the args below, we have to access the
        # variable as a reference, otherwise a new local variable is
        # created inside a function scope. So we create a dummy dict
        # which wraps the real value. This can be done better in Python 3.
        stored_order_by = {
            'value': []
        }

        # We temporary replace order_by method on the queryset to hijack
        # the arguments passed to the order_by so that we can pass them
        # to _after_apply_sorting.
        obj_list_order_by = obj_list.order_by

        def order_by(*args):
            stored_order_by['value'] = args
            return obj_list_order_by(*args)

        obj_list.order_by = order_by

        try:
            sorted_queryset = super(BaseResource, self).apply_sorting(obj_list, options)
        finally:
            # Restore the original order_by method. Just to be sure
            # if it is reused somewhere else as well.
            obj_list.order_by = obj_list_order_by

        sorted_queryset = self._after_apply_sorting(sorted_queryset, options, stored_order_by['value'])

        # Restore the count of all objects.
        sorted_queryset._nonfiltered_count = nonfiltered_count

        return sorted_queryset

    def authorized_read_list(self, object_list, bundle):
        # Since authorization filter is applied after the generic filters have been
        # applied, we need to account for the difference that the auth filter causes
        nonfiltered_count = object_list._nonfiltered_count
        count = object_list.count()
        filtered_queryset = super(BaseResource, self).authorized_read_list(object_list, bundle)
        delta = count - filtered_queryset.count()
        filtered_queryset._nonfiltered_count = nonfiltered_count - delta

        return filtered_queryset

    # A hook so that queryset can be modified before count for _nonfiltered_count is taken
    # (for filtering which should not be exposed through dataTables)
    def _before_apply_filters(self, request, queryset):
        return queryset

    def apply_filters(self, request, applicable_filters):
        queryset = self.get_object_list(request)
        queryset = self._before_apply_filters(request, queryset)
        filtered_queryset = queryset.filter(**applicable_filters)

        f = request.GET.get('filter', None)
        if f and getattr(self._meta, 'global_filter', None):
            # TODO: Q objects should transform registry field names automatically, so that we do not have to call registry_expand_proxy_field
            qs = [query.Q(**{filtered_queryset.registry_expand_proxy_field('%s__icontains' % field): f}) for field in self._meta.global_filter]
            filter_query = qs[0]
            for q in qs[1:]:
                filter_query |= q
            filtered_queryset = filtered_queryset.filter(filter_query).distinct()

        # We store count of all objects before filtering to be able to provide it in paginator (used in dataTables)
        filtered_queryset._nonfiltered_count = queryset.count()

        return filtered_queryset
