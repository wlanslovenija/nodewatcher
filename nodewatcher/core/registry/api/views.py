from django.db.models import constants
from django.contrib.auth import models as auth_models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import functions as geo_functions

from rest_framework import viewsets
from guardian import shortcuts

from .. import expression


class RegistryRootViewSetMixin(object):
    def get_queryset(self):
        queryset = super(RegistryRootViewSetMixin, self).get_queryset()
        return self.get_registry_queryset(queryset)

    def get_registry_queryset(self, queryset):
        # Apply projection.
        for field in self.request.query_params.getlist('fields'):
            try:
                field_name, queryset = apply_registry_field(field, queryset)
            except ValueError:
                # Ignore invalid field projections.
                pass

        # Apply filters.
        for argument, value in self.request.query_params.items():
            if argument in ('fields', 'limit', 'offset', 'ordering'):
                continue

            try:
                queryset = apply_registry_filter(argument, value, queryset)
            except ValueError:
                # Ignore invalid filters as they may be some other query arguments.
                pass

        # Apply ordering.
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))

        # Apply permission-based maintainer filter.
        maintainer = self.request.query_params.get('maintainer', None)
        if maintainer:
            try:
                maintainer_user = auth_models.User.objects.get(username=maintainer)
                queryset = shortcuts.get_objects_for_user(maintainer_user, [], queryset, with_superuser=False, accept_global_perms=False)
            except auth_models.User.DoesNotExist:
                queryset = queryset.none()

        return queryset


def apply_registry_filter(path, value, queryset):
    """
    Applies a given registry filter to the given queryset.

    :param path: Field path
    :param value: Filtered value
    :param queryset: Queryset to apply the filter to
    :return: An updated queryset
    """

    parser = expression.LookupExpressionParser()
    info = parser.parse(path)

    queryset = queryset.regpoint(info.registration_point)
    condition = '%s%s%s' % (info.registry_id.replace('.', '_'), constants.LOOKUP_SEP, constants.LOOKUP_SEP.join(info.field or []))
    queryset = queryset.registry_filter(**{condition: value})

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

    queryset = queryset.regpoint(info.registration_point).registry_fields(**{field_name: info})
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
