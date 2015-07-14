from django.db import models as django_models

from tastypie import fields
from tastypie import authorization as api_authorization, authentication as api_authentication

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import api
from nodewatcher.core.frontend.api import fields as api_fields
from nodewatcher.core.generator import models as generator_models
from nodewatcher.modules.frontend.list import resources


class BuildResultAuthorization(api_authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class NodeResource(resources.NodeResource):
    class Meta(resources.NodeResource.Meta):
        fields = ('uuid', 'name')

    def _build_reverse_url(self, name, args=None, kwargs=None):
        # We fake it here and set it to the same as registered resource.
        # It is not set because we have not registered this node resource.
        self._meta.urlconf_namespace = resources.NodeResource._meta.urlconf_namespace
        return super(NodeResource, self)._build_reverse_url(name, args=args, kwargs=kwargs)


class BuildChannelResource(api.BaseResource):
    name = fields.CharField('name')
    description = fields.CharField('description')
    default = fields.BooleanField('default')

    class Meta:
        resource_name = 'build_channel'
        queryset = generator_models.BuildChannel.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        fields = ('name', 'description', 'default')


class BuildVersionResource(api.BaseResource):
    name = fields.CharField('name')

    class Meta:
        resource_name = 'build_version'
        queryset = generator_models.BuildVersion.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        fields = ('name',)


class BuilderResource(api.BaseResource):
    platform = fields.CharField('platform')
    architecture = fields.CharField('architecture')
    version = api_fields.ToOneField(BuildVersionResource, 'version', full=True)

    class Meta:
        resource_name = 'builder'
        queryset = generator_models.Builder.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        fields = ('platform', 'architecture', 'version')


class BuildResultFileResource(api.BaseResource):
    file = fields.FileField('file')
    checksum_md5 = fields.CharField('checksum_md5')
    checksum_sha256 = fields.CharField('checksum_sha256')

    class Meta:
        resource_name = 'build_result_file'
        queryset = generator_models.BuildResultFile.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ('get',)
        # TODO: Authorization


class BuildResultResource(api.BaseResource):
    node = api_fields.ToOneField(NodeResource, 'node', full=True)
    build_channel = api_fields.ToOneField(BuildChannelResource, 'build_channel', full=True)
    builder = api_fields.ToOneField(BuilderResource, 'builder', full=True)
    files = fields.ToManyField(BuildResultFileResource, 'files', full=True, use_in='detail')
    build_log = fields.CharField('build_log', use_in='detail')
    config = fields.DictField('config', use_in='detail')

    class Meta:
        queryset = generator_models.BuildResult.objects.prefetch_related(
            django_models.Prefetch(
                'node',
                queryset=core_models.Node.objects.regpoint('config').registry_fields(
                    name='core.general#name',
                )
            ),
            'build_channel',
            'builder',
            'builder__version',
        # noqa (PEP8 ignore indentation)
        # We have to have some ordering so that pagination works correctly.
        # Otherwise SKIP and LIMIT does not necessary return expected pages.
        # Later calls to order_by override this so if user specifies an order
        # things work as expected as well.
        ).order_by('uuid')
        resource_name = 'build_result'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        ordering = ('uuid', 'node', 'build_channel', 'builder', 'status', 'created')
        # TODO: How can we generate string from registry, without hardcoding registry relations?
        global_filter = ('uuid', 'node__config_core_generalconfig__name', 'build_channel__name', 'builder__version__name', 'status')
        authentication = api_authentication.SessionAuthentication()
        authorization = BuildResultAuthorization()

    def _after_apply_sorting(self, obj_list, options, order_by_args):
        # We want to augment sorting so that it is always sorted at the end by "uuid" to have a defined order
        # even for keys which are equal between multiple objects. This is necessary for pagination to work correctly,
        # because SKIP and LIMIT works well for pagination only when all objects have a defined order.
        extended_order = list(order_by_args) + ['uuid']
        return obj_list.order_by(*extended_order)
