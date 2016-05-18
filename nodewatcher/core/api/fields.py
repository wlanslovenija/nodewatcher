import ujson

from tastypie import fields as tastypie_fields, exceptions as tastypie_exceptions


class ApiNameMixin(object):
    def get_api_name(self):
        if getattr(self, 'api_name', None) is not None:
            return self.api_name
        if getattr(self, '_resource', None) and self._resource._meta.api_name is not None:
            return self._resource._meta.api_name
        return None


class FieldInUsePathMixin(object):
    """
    Support for field filtering.
    """

    def contribute_to_class(self, cls, name):
        from . import resources

        super(FieldInUsePathMixin, self).contribute_to_class(cls, name)

        # Update use_in in order to support field filtering.
        self.use_in = resources.BaseResource.field_use_in_factory(
            name,
            self.use_in
        )

    def dehydrate(self, bundle, for_list=True):
        # Because bundle.request is the only state which is passed through all
        # dehydration process, we are using it to pass the current path while we
        # are walking the related resources. This is needed when selecting fields
        # in field_use_in_factory to determine to select a field or not.

        if not hasattr(bundle.request, '_field_in_use_path'):
            bundle.request._field_in_use_path = []

        bundle.request._field_in_use_path.append(self.instance_name)
        try:
            return super(FieldInUsePathMixin, self).dehydrate(bundle, for_list)
        finally:
            bundle.request._field_in_use_path.pop()


class ToOneField(FieldInUsePathMixin, ApiNameMixin, tastypie_fields.ToOneField):
    """
    Extended tastypie ToOneField with support for nested schema and field
    filtering.
    """

    def build_schema(self):
        return {
            'fields': self.to_class(self.get_api_name()).build_schema()['fields'],
        }


class ManyToManyField(FieldInUsePathMixin, ApiNameMixin, tastypie_fields.ManyToManyField):
    """
    Extended tastypie ManyToManyField with support field filtering.
    """


class RegistryRelationField(ToOneField):
    """
    Tastypie field for registry relation field.
    """

    dehydrated_type = 'registry'

    def __init__(self, to, attribute, default=tastypie_fields.NOT_PROVIDED, null=False, blank=False, readonly=False, unique=False, help_text=None, verbose_name=None):
        """
        The ``to`` argument should point to a ``Resource`` class, not to a ``document``. Required.
        """

        super(RegistryRelationField, self).__init__(
            to=to,
            attribute=attribute,
            default=default,
            null=null,
            blank=blank,
            readonly=readonly,
            unique=unique,
            verbose_name=verbose_name,
            full=True,
        )

        self._help_text = help_text

    @property
    def help_text(self):
        if not self._help_text:
            self._help_text = "Registry model (%s)" % (self.to_class(self.get_api_name())._meta.resource_name,)
        return self._help_text


class RegistryMultipleRelationField(ManyToManyField):
    """
    Tastypie field for registry multiple relation field.
    """

    dehydrated_type = 'registry'

    def __init__(self, to, attribute, default=tastypie_fields.NOT_PROVIDED, null=False, blank=False, readonly=False, unique=False, help_text=None, verbose_name=None):
        """
        The ``to`` argument should point to a ``Resource`` class, not to a ``document``. Required.
        """

        super(RegistryMultipleRelationField, self).__init__(
            to=to,
            attribute=attribute,
            default=default,
            null=null,
            blank=blank,
            readonly=readonly,
            unique=unique,
            verbose_name=verbose_name,
            full=True,
        )

        self._help_text = help_text

    @property
    def help_text(self):
        if not self._help_text:
            self._help_text = "Registry model (%s)" % (self.to_class(self.get_api_name())._meta.resource_name,)
        return self._help_text


class GeoJSON(str):
    __slots__ = ()

    def __json__(self):
        return self


class GeometryField(tastypie_fields.ApiField):
    """
    Tastypie field for properly serializing geometry fields with support for
    leveraging precomputed GeoJSON fields specified in the queryset.
    """

    dehydrated_type = 'geometry'
    help_text = 'GeoJSON geometry data.'

    def __init__(self, *args, **kwargs):
        super(GeometryField, self).__init__(*args, **kwargs)

    def hydrate(self, bundle):
        value = super(GeometryField, self).hydrate(bundle)
        if value is None:
            return value
        return ujson.dumps(value)

    def dehydrate(self, bundle, for_list=True):
        if self.attribute is not None:
            # We require the queryset to populate the models with a _geojson attribute
            # which will be used here as an optimization, so expensive GDAL conversions
            # will not be needed.
            try:
                value = getattr(bundle.obj, '%s_geojson' % self.attribute)
                if value is not None:
                    return GeoJSON(value)
                return None
            except AttributeError:
                # We explicitly force users to perform this optimization.
                raise tastypie_exceptions.ApiFieldError('Missing attribute "%s_geojson" on model. Using a GeometryField in your API resource requires the use of geojson() on the queryset!' % self.attribute)

        if self.has_default():
            return self.default
        else:
            return None
