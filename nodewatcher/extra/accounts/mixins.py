import collections

from django.conf import settings
from django.contrib import auth, messages
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from . import decorators


class AuthenticatedRequiredMixin(object):
    redirect_field_name = auth.REDIRECT_FIELD_NAME

    def message(self, user):
        return _("You have to be logged in while accessing the previous page. Please login to continue.")

    def message_level(self, user):
        return messages.ERROR

    def redirect_url(self, user):
        return settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        return decorators.authenticated_required(
            function=super(AuthenticatedRequiredMixin, self).dispatch,
            message_func=self.message,
            message_level_func=self.message_level,
            redirect_url_func=self.redirect_url,
            redirect_field_name=self.redirect_field_name,
        )(request, *args, **kwargs)


class AnonymousRequiredMixin(object):
    redirect_field_name = auth.REDIRECT_FIELD_NAME

    def message(self, user):
        return _("You should not be logged in while accessing the previous page.")

    def message_level(self, user):
        return messages.ERROR

    def redirect_url(self, user):
        return settings.LOGIN_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        return decorators.anonymous_required(
            function=super(AnonymousRequiredMixin, self).dispatch,
            message_func=self.message,
            message_level_func=self.message_level,
            redirect_url_func=self.redirect_url,
            redirect_field_name=self.redirect_field_name,
        )(request, *args, **kwargs)


# Similar to django guardian's PermissionRequiredMixin, but uses our permissions decorator.
class PermissionRequiredMixin(object):
    redirect_field_name = auth.REDIRECT_FIELD_NAME
    raise_exception = False
    accept_global_perms = False
    permission_required = None
    permission_object = None

    def message(self, user):
        if user.is_authenticated():
            return _("You do not have necessary permission to access the previous page.")
        else:
            return _("You have to be logged in while accessing the previous page. Please login to continue.")

    def message_level(self, user):
        return messages.ERROR

    def redirect_url(self, user):
        if user.is_authenticated():
            return settings.LOGIN_REDIRECT_URL
        else:
            return settings.LOGIN_URL

    def get_required_permissions(self, request=None):
        if isinstance(self.permission_required, basestring):
            perms = [self.permission_required]
        elif isinstance(self.permission_required, collections.Iterable):
            perms = [p for p in self.permission_required]
        else:
            raise exceptions.ImproperlyConfigured("'PermissionRequiredMixin' requires "
                                                  "'permission_required' attribute to be set to "
                                                  "'<app_label>.<permission codename>' but is set to '%s' instead"
                                                  % self.permission_required)
        return perms

    def get_permission_object(self):
        if self.permission_object:
            return self.permission_object
        return (hasattr(self, 'get_object') and self.get_object() or getattr(self, 'object', None))

    def dispatch(self, request, *args, **kwargs):
        return decorators.permission_required(
            self.get_required_permissions(request),
            function=super(PermissionRequiredMixin, self).dispatch,
            message_func=self.message,
            message_level_func=self.message_level,
            redirect_url_func=self.redirect_url,
            redirect_field_name=self.redirect_field_name,
            raise_exception=self.raise_exception,
            obj_func=self.get_permission_object,
            accept_global_perms=self.accept_global_perms,
        )(request, *args, **kwargs)
