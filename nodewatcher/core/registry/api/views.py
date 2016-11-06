from django.db import models as django_models
from django.db.models import constants
from django.contrib.auth import models as auth_models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import functions as geo_functions
from django.core import exceptions as django_exceptions

from rest_framework import viewsets
from guardian import shortcuts

from .. import expression, exceptions

# Exports.
__all__ = [
    'RegistryRootViewSetMixin'
]


class RegistryRootViewSetMixin(object):
    def get_queryset(self):
        queryset = super(RegistryRootViewSetMixin, self).get_queryset()

        registry_root_fields = getattr(self, 'registry_root_fields', None)
        if registry_root_fields is None:
            return self.get_registry_queryset(queryset)
        else:
            for field in registry_root_fields:
                registry_queryset = queryset.model._meta.get_field(field).related_model.objects.all()
                queryset = queryset.prefetch_related(
                    django_models.Prefetch(
                        field,
                        queryset=self.get_registry_queryset(registry_queryset, field=field)
                    )
                )

            return queryset

    def get_registry_queryset(self, queryset, field=None):
        if field is None:
            argument_name = lambda name: name
        else:
            argument_name = lambda name: '%s__%s' % (field, name)

        # Apply projection.
        for field in self.request.query_params.getlist(argument_name('fields')):
            try:
                field_name, queryset = apply_registry_field(field, queryset)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError):
                # Ignore invalid field projections.
                pass

        # Apply filter expression.
        filters = self.request.query_params.get(argument_name('filters'), None)
        if filters:
            try:
                parser = expression.FilterExpressionParser(queryset.model, disallow_sensitive=True)
                queryset = parser.parse(filters).apply(queryset)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError, KeyError):
                # Ignore invalid filters.
                pass

        # Apply ordering.
        ordering = self.request.query_params.get(argument_name('ordering'), None)
        if ordering:
            try:
                queryset = queryset.order_by(*ordering.split(','), disallow_sensitive=True)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError):
                pass

        # Apply permission-based filter.
        has_permissions = self.request.query_params.get(argument_name('has_permissions'), None)
        if has_permissions:
            try:
                has_permissions_user = auth_models.User.objects.get(username=has_permissions)
                queryset = shortcuts.get_objects_for_user(has_permissions_user, [], queryset, with_superuser=False, accept_global_perms=False)
            except auth_models.User.DoesNotExist:
                queryset = queryset.none()

        return queryset


def apply_registry_field(field_specifier, queryset):
    """
    Applies a given registry field specifier to the given queryset.

    :param field_specifier: Field specifier string
    :param queryset: Queryset to apply the field specifier to
    :return: An updated queryset
    """

    parser = expression.LookupExpressionParser()
    info = parser.parse(field_specifier)
    field_name = info.name

    queryset = queryset.registry_fields(**{field_name: info})
    for field in queryset.model._meta.virtual_fields:
        if field.name != field_name:
            continue

        # Check if the model has any Geometry fields and perform GeoJSON annotations.
        for dst_field in field.src_model._meta.get_fields():
            if isinstance(dst_field, geo_models.GeometryField):
                field_path = '%s%s%s' % (queryset.registry_expand_proxy_field(field_name), constants.LOOKUP_SEP, dst_field.name)
                annotation_name = '%s_annotations_%s' % (field_name, field_path)
                queryset = queryset.annotate(**{annotation_name: geo_functions.AsGeoJSON(field_path)})

                container = getattr(field, '_registry_annotations', {})
                container['%s_geojson' % dst_field.name] = annotation_name
                field._registry_annotations = container

    return field_name, queryset
