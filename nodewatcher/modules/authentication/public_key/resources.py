from tastypie import authorization as api_authorization, authentication as api_authentication

from nodewatcher.core.frontend import api

from . import models


class UserAuthenticationKeyAuthorization(api_authorization.Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class UserAuthenticationKeyResource(api.BaseResource):

    class Meta:
        queryset = models.UserAuthenticationKey.objects.all().order_by('pk')
        resource_name = 'user_authentication_key'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        ordering = ('pk', 'name', 'fingerprint', 'created')
        global_filter = ('name', 'fingerprint', 'created')
        authentication = api_authentication.SessionAuthentication()
        authorization = UserAuthenticationKeyAuthorization()
