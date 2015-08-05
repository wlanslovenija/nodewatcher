from tastypie import resources, fields

from .pool import pool


class StatisticsResource(object):
    """
    A statistics resource that is exposed via the statistics API endpoint.
    """

    name = None
    description = None

    def get_name(self):
        """
        Returns the resource name.
        """

        return self.name

    def get_header(self):
        """
        Returns header data, which should describe the used fields somehow.
        """

        return {}

    @property
    def header(self):
        return self.get_header()

    def get_statistics(self):
        """
        Returns a list of statistics. This method must be implemented by resource
        subclasses.
        """

        raise NotImplementedError

    @property
    def statistics(self):
        return self.get_statistics()


class StatisticsPoolResource(resources.NamespacedModelMixin, resources.Resource):
    name = fields.CharField(attribute='name')
    description = fields.CharField(attribute='description')
    header = fields.DictField(attribute='header', use_in='detail')
    statistics = fields.ListField(attribute='statistics', use_in='detail')

    class Meta:
        resource_name = 'statistics'
        object_class = StatisticsResource
        allowed_methods = ('get',)

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, resources.Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.get_name()
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.get_name()

        return kwargs

    def get_object_list(self, request):
        return pool.get_all_resources()

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        return pool.get_resource(kwargs['pk'])
