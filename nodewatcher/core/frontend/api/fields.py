import ujson

from tastypie import fields as tastypie_fields, exceptions as tastypie_exceptions


class ApiNameMixin(object):
    def get_api_name(self):
        if getattr(self, 'api_name', None) is not None:
            return self.api_name
        if getattr(self, '_resource', None) and self._resource._meta.api_name is not None:
            return self._resource._meta.api_name
        return None


class RegistryRelationField(ApiNameMixin, tastypie_fields.ToOneField):
    """
    Tastypie field for registry relation field.
    """

    is_related = False
    dehydrated_type = 'registry'

    def __init__(self, to, attribute, default=tastypie_fields.NOT_PROVIDED, null=False, blank=False, readonly=False, unique=False, help_text=None):
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
            full=True,
        )

        self._help_text = help_text

    @property
    def help_text(self):
        if not self._help_text:
            self._help_text = "Registry model (%s)." % (self.to_class(self.get_api_name())._meta.resource_name,)
        return self._help_text

    def build_schema(self):
        return {
            'fields': self.to_class(self.get_api_name()).build_schema()['fields'],
        }


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
                    return ujson.loads(value)
                return None
            except AttributeError:
                # We explicitly force users to perform this optimization.
                raise tastypie_exceptions.ApiFieldError('Missing attribute "%s_geojson" on model. Using a GeometryField in your API resource requires the use of geojson() on the queryset!' % self.attribute)

        if self.has_default():
            return self.default
        else:
            return None
