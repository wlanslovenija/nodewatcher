from django import shortcuts
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.core import urlresolvers
from django.utils import functional as functional_utils
from django.views.generic import simple as generic_simple

from registration import views as registration_views

from web.account import decorators
from web.account import forms
from web.nodes import feeds
from web.nodes import sitemaps

# Legacy feeds (GeoDjango feeds have not yet been upgraded to new code)
feeds_dict = {
  'active' : feeds.ActiveNodes,
}

sitemaps = {
  'nodes'  : sitemaps.NodeSitemap,
  'static' : sitemaps.StaticSitemap,
  'root'   : sitemaps.RootPageSitemap,
}

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
      'backend': 'web.account.regbackend.ProfileBackend',
    }, name='registration_activate'),
  url(r'^register/$', decorators.anonymous_required(function=registration_views.register), {
      'backend': 'web.account.regbackend.ProfileBackend',
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
  url(r'^login/$', 'web.account.views.login', name='auth_login'),
  url(r'^logout/$', 'web.account.views.logout_redirect', name='auth_logout'),
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
  url(r'^$', 'web.account.views.account', name='user_account'),
)

urlpatterns = patterns('',
  # Nodes list
  url(r'^$', 'web.nodes.views.nodes', name = 'nodes_list'),
  url(r'^network/nodes/$', lambda request: shortcuts.redirect('nodes_list', permanent=False)), # Nodes list is currently hard-coded as primary landing section, this is not necessary so
  url(r'^nodes/list/$', lambda request: shortcuts.redirect('nodes_list', permanent=True)), # Legacy
  url(r'^nodes/node_list/$', lambda request: shortcuts.redirect('nodes_list', permanent=True)), # Legacy

  # Global nodes information
  url(r'^network/statistics/$', 'web.nodes.views.statistics', name = 'network_statistics'),
  url(r'^nodes/statistics/$', lambda request: shortcuts.redirect('network_statistics', permanent=True)), # Legacy
  url(r'^network/events/$', 'web.nodes.views.global_events', name = 'network_events'),
  url(r'^nodes/events/global/$', lambda request: shortcuts.redirect('network_events', permanent=True)), # Legacy
  url(r'^network/clients/$', 'web.nodes.views.gcl', name = 'network_clients'),
  url(r'^nodes/gcl/$', lambda request: shortcuts.redirect('network_clients', permanent=True)), # Legacy
  url(r'^network/topology/$', 'web.nodes.views.topology', name = 'network_topology'),
  url(r'^nodes/topology/$', lambda request: shortcuts.redirect('network_topology', permanent=True)), # Legacy
  url(r'^network/map/$', 'web.nodes.views.map', name = 'network_map'),
  url(r'^nodes/map/$', lambda request: shortcuts.redirect('network_map', permanent=True)), # Legacy
  
  # Node maintainers
  url(r'^my/nodes/$', 'web.nodes.views.my_nodes', name = 'my_nodes'),
  url(r'^nodes/my_nodes/$', lambda request: shortcuts.redirect('my_nodes', permanent=True)), # Legacy
  url(r'^my/new/$', 'web.nodes.views.node_new', name = 'new_node'),
  url(r'^nodes/new/$', lambda request: shortcuts.redirect('new_node', permanent=True)), # Legacy
  url(r'^my/whitelist/$', 'web.nodes.views.whitelisted_mac', name = 'my_whitelist'),
  url(r'^nodes/whitelisted_mac/$', lambda request: shortcuts.redirect('my_whitelist', permanent=True)), # Legacy
  url(r'^my/whitelist/remove/(?P<item_id>\d+)/$', 'web.nodes.views.unwhitelist_mac', name = 'my_whitelist_remove'),  
  url(r'^my/events/$', 'web.nodes.views.event_list', name = 'my_events'),
  url(r'^my/events/subscribe/$', 'web.nodes.views.event_subscribe', name = 'my_events_subscribe'),
  url(r'^my/events/unsubscribe/(?P<subscription_id>\d+)/$', 'web.nodes.views.event_unsubscribe', name = 'my_events_unsubscribe'),
  
  # Node itself, public
  # (Those views should have permalinks defined and are also those which have be_robust set to True)
  url(r'^node/(?P<node>[^/]+)/$', 'web.nodes.views.node', name = 'view_node'),
  url(r'^nodes/node/(?P<node>.+)/$', lambda request, node: shortcuts.redirect('view_node', permanent=True, node=node)), # Legacy
  url(r'^node/(?P<node>[^/]+)/events/$', 'web.nodes.views.node_events', name = 'view_node_events'),
  url(r'^nodes/events/(?P<node>.+)/$', lambda request, node: shortcuts.redirect('view_node_events', permanent=True, node=node)), # Legacy
  
  # Node itself, private
  url(r'^node/(?P<node>[^/]+)/packages/$', 'web.nodes.views.package_list', name = 'view_node_packages'),
  url(r'^nodes/installed_packages/(?P<node>.+)/$', lambda request, node: shortcuts.redirect('view_node_packages', permanent=True, node=node)), # Legacy
  
  # Node manipulation
  url(r'^node/(?P<node>[^/]+)/edit/$', 'web.nodes.views.node_edit', name = 'edit_node'),
  url(r'^node/(?P<node>[^/]+)/remove/$', 'web.nodes.views.node_remove', name = 'remove_node'),
  url(r'^node/(?P<node>[^/]+)/reset/$', 'web.nodes.views.node_reset', name = 'reset_node'),
  url(r'^node/(?P<node>[^/]+)/renumber/$', 'web.nodes.views.node_renumber', name = 'renumber_node'),
  url(r'^node/(?P<node>[^/]+)/subnet/allocate/$', 'web.nodes.views.node_allocate_subnet', name = 'allocate_subnet'),
  url(r'^node/(?P<node>[^/]+)/subnet/(?P<subnet_id>\d+)/deallocate/$', 'web.nodes.views.node_deallocate_subnet', name = 'remove_subnet'),
  url(r'^node/(?P<node>[^/]+)/subnet/(?P<subnet_id>\d+)/edit/$', 'web.nodes.views.node_edit_subnet', name = 'edit_subnet'),
  
  # Graphs
  url(r'^graphs/(?P<graph_id>-?\d+)/(?P<timespan>.+)/$', 'web.monitor.views.graph_image', name = 'graph_image'),
  
  # Feeds
  url(r'^feeds/whitelist/$', 'web.nodes.views.whitelist'),
  url(r'^feeds/rss/events(?:/(?P<username>[\w.@+-]+))?/$', feeds.LatestEvents(), name = 'events_feed'),
  url(r'^feeds/rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', { 'feed_dict' : feeds_dict }, name = 'feeds'),

  # Pools
  url(r'^pools/$', 'web.nodes.views.pools', name = 'pools'),
  url(r'^pools/txt/$', 'web.nodes.views.pools_text', name = 'pools_text'),

  # Sitemap
  url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps' : sitemaps }),

  # Generator
  url(r'^generator/request/(?P<node>.*)/$', 'web.generator.views.request', name = 'generate_node'),

  # Accounts
  (r'^account/', include(account_patterns)),
  url(r'^user/(?P<username>[\w.@+-]+)/$', 'web.account.views.user', name = 'user_page'),
)

handler403 = 'web.nodes.views.forbidden_view'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

if getattr(settings, 'DEBUG', False):
  urlpatterns += patterns('',
    (r'^403/$', handler403),
    (r'^404/$', handler404),
    (r'^500/$', handler500),
  )

if getattr(settings, 'DEBUG', False) and not settings.MEDIA_URL.startswith('http'):
  # Server static files with Django when running in debug mode and MEDIA_URL is local
  
  static_patterns = patterns('',
    url(r'^(?P<path>(?:css|graphs|images|js|wlansi)/.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
  )
  
  media_url = settings.MEDIA_URL.lstrip('/')
  urlpatterns += patterns('',
    (r'^%s' % media_url, include(static_patterns)),
  )
