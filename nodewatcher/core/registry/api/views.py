from django.db.models import constants
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models import functions as geo_functions

from rest_framework import viewsets

FIELD_SEPARATOR = '|'


class RegistryRootViewSetMixin(object):
    def get_queryset(self):
        queryset = super(RegistryRootViewSetMixin, self).get_queryset()
        return self.get_registry_queryset(queryset)

    def get_registry_queryset(self, queryset):
        # Apply projection.
        for field in self.request.query_params.getlist('fields'):
            field_name, queryset = apply_registry_field(field, queryset)

        # Apply filters.
        for argument, value in self.request.query_params.items():
            if argument in ('fields', 'limit', 'offset'):
                continue

            try:
                queryset = apply_registry_filter(argument, value, queryset)
            except ValueError:
                # Ignore invalid filters as they may be some other query arguments.
                pass

        return queryset


def apply_registry_filter(path, value, queryset):
    """
    Applies a given registry filter to the given queryset.

    :param path: Field path
    :param value: Filtered value
    :param queryset: Queryset to apply the filter to
    :return: An updated queryset
    """

    atoms = path.split(FIELD_SEPARATOR)

    # Parse registry point.
    if atoms:
        registry_point = atoms.pop(0)
        queryset = queryset.regpoint(registry_point)

        # Parse registry item identifier.
        if atoms:
            registry_id = atoms.pop(0)
            registry_id = registry_id.replace('.', '_')
            condition = '%s__%s' % (registry_id, constants.LOOKUP_SEP.join(atoms))
            queryset = queryset.registry_filter(**{condition: value})

    return queryset


def apply_registry_field(field_specifier, queryset):
    """
    Applies a given registry field specifier to the given queryset.

    :param field_specifier: Field specifier string
    :param queryset: Queryset to apply the field specifier to
    :return: An updated queryset
    """

    atoms = field_specifier.split(FIELD_SEPARATOR)
    field_name = None

    # Parse registry point.
    if atoms:
        registry_point = atoms.pop(0)
        queryset = queryset.regpoint(registry_point)

        # Parse registry item identifier.
        if atoms:
            registry_id = atoms.pop(0)

            # Parse optional field path specifier.
            field_path = ''
            if atoms:
                field_path = atoms.pop(0)

            field_name = '%s%s%s' % (registry_point, registry_id.replace('.', '_'), field_path.replace('.', '_'))
            queryset = queryset.registry_fields(**{field_name: '%s%s' % (registry_id, ('#%s' % field_path) if field_path else '')})
            for field in queryset.model._meta.virtual_fields:
                if field.name != field_name:
                    continue

                # Check if the model has any Geometry fields and perform GeoJSON annotations.
                for dst_field in field.src_model._meta.get_fields():
                    if isinstance(dst_field, geo_models.GeometryField):
                        field_path = '%s__%s' % (queryset.registry_expand_proxy_field(field_name), dst_field.name)
                        annotation_name = '%s_annotations_%s' % (field_name, field_path)
                        queryset = queryset.annotate(**{annotation_name: geo_functions.AsGeoJSON(field_path)})

                        container = getattr(field, '_registry_annotations', {})
                        container['%s_geojson' % dst_field.name] = annotation_name
                        field._registry_annotations = container

    return field_name, queryset
