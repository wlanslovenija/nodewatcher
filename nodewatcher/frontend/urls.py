from django import shortcuts
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.core import urlresolvers
from django.utils import functional as functional_utils
from django.views.generic import simple as generic_simple

from registration import views as registration_views

from frontend.account import decorators
from frontend.account import forms

# We pass redirect targets as a lazy unicode string as we are backreferencing.
# We wrap views with custom decorators to force anonymous and authenticated access to them (it is strange to
# try to register a new account while still logged in with another account). We redirect the user away and tell
# the user what has happened with messages.
# Some views use those decorators already so they are not used here. `logout_redirect` does not require
# authenticated access on purpose.
# We use custom login and logout views which give messages to the user explaining what has happened with login
# and logout. We do not assume the user understands what is happening behind the scenes.
account_patterns = patterns('',
  url(r'^activate/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
      'template': 'registration/activation_complete.html',
    }, name='registration_activation_complete'),
  url(r'^activate/(?P<activation_key>\w+)/$', decorators.anonymous_required(function=registration_views.activate), {
      'backend': 'frontend.account.regbackend.ProfileBackend',
    }, name='registration_activate'),
  url(r'^register/$', decorators.anonymous_required(function=registration_views.register), {
      'backend': 'frontend.account.regbackend.ProfileBackend',
    }, name='registration_register'),
  url(r'^register/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
      'template': 'registration/registration_complete.html',
    }, name='registration_complete'),
  url(r'^register/closed/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
      'template': 'registration/registration_closed.html',
    }, name='registration_disallowed'),
  url(r'^email/change/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
      'template': 'registration/email_change_complete.html',
    }, name='email_change_complete'),
  url(r'^login/$', 'frontend.account.views.login', name='auth_login'),
  url(r'^logout/$', 'frontend.account.views.logout_redirect', name='auth_logout'),
  url(r'^password/change/$', decorators.authenticated_required(function=auth_views.password_change), {
      'post_change_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_change_done'),
      'password_change_form': forms.PasswordChangeForm,
    }, name='auth_password_change'),
  url(r'^password/change/complete/$', decorators.authenticated_required(function=auth_views.password_change_done), name='auth_password_change_done'),
  url(r'^password/reset/$', decorators.anonymous_required(function=auth_views.password_reset), {
      'email_template_name': 'registration/password_reset_email.txt',
      'password_reset_form': forms.PasswordResetForm,
      'post_reset_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_reset_done'),
    }, name='auth_password_reset'),
  url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', decorators.anonymous_required(function=auth_views.password_reset_confirm), {
      'set_password_form': forms.SetPasswordForm,
      'post_reset_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_reset_complete'),
    }, name='auth_password_reset_confirm'),
  url(r'^password/reset/complete/$', decorators.anonymous_required(function=auth_views.password_reset_complete), name='auth_password_reset_complete'),
  url(r'^password/reset/done/$', decorators.anonymous_required(function=auth_views.password_reset_done), name='auth_password_reset_done'),
  url(r'^$', 'frontend.account.views.account', name='user_account'),
)

urlpatterns = patterns('',
  # Node lists
  url(r'^$', 'frontend.nodes.views.nodes', name = 'nodes_list'),

  # Node maintainers
  url(r'^my/new$', 'frontend.nodes.views.node_new', name = 'new_node'),

  # Node itself, public
  # (Those views should have permalinks defined and are also those which have be_robust set to True)
  url(r'^node/(?P<node>[^/]+)$', 'frontend.nodes.views.node_display', name = 'view_node'),

  # Node manipulation
  url(r'^node/(?P<node>[^/]+)/edit$', 'frontend.nodes.views.node_edit', name = 'edit_node'),

  # Registry
  (r'^registry/', include('frontend.registry.urls', namespace = 'registry')),

  # Accounts
  (r'account/', include(account_patterns)),
  url(r'^user/(?P<username>[\w.@+-]+)/$', 'frontend.account.views.user', name = 'user_page'),
)

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
if getattr(settings, 'DEBUG', False):
  urlpatterns += patterns('',
    (r'^404/$', handler404),
    (r'^500/$', handler500),
  )

if getattr(settings, 'DEBUG', None) and not settings.MEDIA_URL.startswith('http'):
  # Server static files with Django when running in debug mode and MEDIA_URL is local
  static_patterns = patterns('',
    url(
      r'^(?P<path>(?:common|css|graphs|images|js|site|stickers|wlanlj|wlansi)/.*)$',
      'django.views.static.serve',
      { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True }
    ),
  )
  
  media_url = settings.MEDIA_URL.lstrip('/')
  urlpatterns += patterns('',
    (r'^%s' % media_url, include(static_patterns)),
  )
