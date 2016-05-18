from tastypie import fields
from tastypie import authorization as api_authorization, authentication as api_authentication

from nodewatcher.core import api

from . import models


class UnknownNodeAuthorization(api_authorization.Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list

        return object_list.none()

    def read_detail(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return True

        return False


class UnknownNodeResource(api.BaseResource):
    uuid = fields.CharField('uuid')
    first_seen = fields.DateTimeField('first_seen')
    last_seen = fields.DateTimeField('last_seen')
    ip_address = fields.CharField('ip_address', null=True)
    certificate = fields.DictField('certificate', null=True)
    origin = fields.CharField('origin')

    class Meta:
        resource_name = 'unknown_node'
        queryset = models.UnknownNode.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        fields = ('uuid', 'first_seen', 'last_seen', 'ip_address', 'certificate', 'origin')
        ordering = ('uuid', 'first_seen', 'last_seen', 'ip_address')
        authentication = api_authentication.SessionAuthentication()
        authorization = UnknownNodeAuthorization()
