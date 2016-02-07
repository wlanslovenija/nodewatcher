from django.core import urlresolvers
from django.conf import urls
from django.contrib import auth
from django.utils import http

from nodewatcher.core.frontend import components

from . import views
from .templatetags import accounts_tags


class AccountsComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(AccountsComponent, cls).get_urls() + [
            urls.url(r'account/', urls.include('nodewatcher.extra.accounts.urls')),
            urls.url(r'^user/(?P<username>[\w.@+-]+)/$', views.user, name='user_page'),
        ]

components.pool.register(AccountsComponent)


def logout_url(menu_entry, context):
    # If a user wants to log out we would like to take her back to the current page
    # or if she has already been redirected to the current page from some other page
    # then to take her back to that page. But only if the target does not require
    # authenticated access which would be after logout denied.
    # TODO: We should probably check not just if url requires authenticated access, but if user has permissions for access
    # TODO: We might move to throwing an exception on permission denied and show an login form inside 403 handler?
    # TODO: Is there a way for accounts_tags.authenticated_required to work with official decorators as well?
    url = urlresolvers.reverse('AccountsComponent:auth_logout')
    redirect_field_name = context.get('REDIRECT_FIELD_NAME', auth.REDIRECT_FIELD_NAME)
    next_url = context.get('next', None) or context.get('request_get_next', None) or context['request'].GET.get(redirect_field_name, None) or context['request'].get_full_path()
    if next_url and not accounts_tags.authenticated_required(next_url):
        url = "%s?%s=%s" % (url, redirect_field_name, http.urlquote(next_url))
    return url

components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Profile"), weight=-100,
    url=lambda menu_entry, context: urlresolvers.reverse('AccountsComponent:user_page', kwargs={'username': context['request'].user.get_username()}),
    visible=lambda menu_entry, request, context: request.user.is_authenticated(),
))
components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Logout"), weight=100,
    url=logout_url,
    visible=lambda menu_entry, request, context: request.user.is_authenticated(),
))


def login_url(menu_entry, context):
    # If a user wants to log in we would like to take her back to the current page
    # or if she has already been redirected to the current page from some other page
    # then to take her back to that page. But only if the target does not require
    # anonymous access which would be after logout denied.
    # TODO: We might move to throwing an exception on permission denied and use 403 handler to explain that user should not be authenticated?
    # TODO: Is there a way for accounts_tags.anonymous_required to work with official decorators as well?
    url = urlresolvers.reverse('AccountsComponent:auth_login')
    redirect_field_name = context.get('REDIRECT_FIELD_NAME', auth.REDIRECT_FIELD_NAME)
    next_url = context.get('next', None) or context.get('request_get_next', None) or context['request'].GET.get(redirect_field_name, None) or context['request'].get_full_path()
    if next_url and not accounts_tags.anonymous_required(next_url):
        url = "%s?%s=%s" % (url, redirect_field_name, http.urlquote(next_url))
    return url

components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Login"),
    url=login_url,
    visible=lambda menu_entry, request, context: request.user.is_anonymous(),
))
components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Register"),
    url=urlresolvers.reverse_lazy('AccountsComponent:registration_register'),
    visible=lambda menu_entry, request, context: request.user.is_anonymous(),
))
