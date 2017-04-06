from django.db import models as django_models
from django.db.models import constants
from django.contrib.auth import models as auth_models
from django.contrib.gis.db import models as geo_models
# This must be imported in this manner as otherwise an incorrect module will be
# imported due to gis.db.models.__init__ importing * from django.db.models.
import django.contrib.gis.db.models.functions as geo_functions
from django.core import exceptions as django_exceptions

from guardian import shortcuts

from .. import expression, exceptions, lookup

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
            for field_name in registry_root_fields:
                field = queryset.model._meta.get_field(field_name)
                queryset = queryset.prefetch_related(
                    django_models.Prefetch(
                        field.name,
                        # Apply projections to subqueryset.
                        queryset=self.get_registry_projection_queryset(
                            field.related_model.objects.all(),
                            field=field
                        )
                    )
                )
                # Apply filters to base queryset.
                queryset = self.get_registry_filter_queryset(queryset, field=field)

            return queryset

    def get_registry_argument_name(self, name, field=None):
        """
        Return name of a registry API argument.

        :param name: Argument name
        :param field: Optional root field instance
        """

        if field is None:
            return name
        else:
            return '{}__{}'.format(field.name, name)

    def get_registry_projection_queryset(self, queryset, field=None):
        """
        Apply registry projection on a queryset.

        The destination queryset must be a registry queryset, otherwise
        this operation will fail.

        :param queryset: Queryset to apply the projection to
        :param field: Optional root field instance
        """

        for field_instance in self.request.query_params.getlist(self.get_registry_argument_name('fields', field)):
            try:
                field_name, queryset = apply_registry_field(field_instance, queryset)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError):
                # Ignore invalid field projections.
                pass

        return queryset

    def get_registry_filter_queryset(self, queryset, field=None):
        """
        Apply registry filters on a queryset.

        The destination queryset can be either a registry queryset or a
        normal queryset. In case it is a normal queryset, the field
        argument must be given.
        """

        if not isinstance(queryset, lookup.RegistryQuerySet) and not field:
            raise ValueError("Non-registry queryset requires 'field' to be set")

        if field is None:
            model = queryset.model
        else:
            model = field.related_model

        # Apply filter expression.
        filters = self.request.query_params.get(self.get_registry_argument_name('filters', field), None)
        if filters:
            try:
                parser = expression.FilterExpressionParser(model, field=field, disallow_sensitive=True)
                queryset = parser.parse(filters).apply(queryset)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError, KeyError):
                # Ignore invalid filters.
                pass

        # Apply ordering.
        ordering = self.request.query_params.get(self.get_registry_argument_name('ordering', field), None)
        if ordering:
            try:
                queryset = lookup.order_by(queryset, ordering.split(','), model,
                                           field=field, disallow_sensitive=True)
            except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError):
                pass

        # Apply permission-based filter.
        has_permissions = self.request.query_params.get(self.get_registry_argument_name('has_permissions', field), None)
        if has_permissions:
            try:
                has_permissions_user = auth_models.User.objects.get(username=has_permissions)
                queryset = shortcuts.get_objects_for_user(has_permissions_user, [], queryset, with_superuser=False, accept_global_perms=False)
            except auth_models.User.DoesNotExist:
                queryset = queryset.none()

        return queryset

    def get_registry_queryset(self, queryset, field=None):
        queryset = self.get_registry_projection_queryset(queryset, field)
        if field is None:
            queryset = self.get_registry_filter_queryset(queryset)

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
