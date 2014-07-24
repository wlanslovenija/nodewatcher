from tastypie import fields as tastypie_fields


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
