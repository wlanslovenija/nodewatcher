from django.conf.urls.defaults import *
from web.nodes.feeds import LatestEvents, ActiveNodes
from web.nodes.sitemaps import NodeSitemap, StaticSitemap, RootPageSitemap
from django.conf import settings
from django.shortcuts import redirect

feeds = {
  'events'  : LatestEvents,
  'active'  : ActiveNodes
}

sitemaps = {
  'nodes'   : NodeSitemap,
  'static'  : StaticSitemap,
  'root'    : RootPageSitemap
}

urlpatterns = patterns('',
  # Node lists
  url(r'^$', 'web.nodes.views.nodes', name = 'nodes_list'),
  url(r'^nodes/list$', lambda request: redirect('nodes_list', permanent=True)), # Legacy
  url(r'^nodes/node_list$', lambda request: redirect('nodes_list', permanent=True)), # Legacy

  # Global nodes information
  url(r'^nodes/statistics$', 'web.nodes.views.statistics', name = 'network_statistics'),
  url(r'^nodes/events', 'web.nodes.views.global_events', name = 'network_events'),
  url(r'^nodes/events/global$', lambda request: redirect('network_events', permanent=True)), # Legacy
  url(r'^nodes/clients', 'web.nodes.views.gcl', name = 'network_clients'),
  url(r'^nodes/gcl$', lambda request: redirect('network_clients', permanent=True)), # Legacy
  url(r'^nodes/topology$', 'web.nodes.views.topology', name = 'network_topology'),
  url(r'^nodes/map$', 'web.nodes.views.map', name = 'network_map'),
  
  # Node maintainers
  url(r'^my/nodes$', 'web.nodes.views.my_nodes', name = 'my_nodes'),
  url(r'^nodes/my_nodes$', lambda request: redirect('my_nodes', permanent=True)), # Legacy
  url(r'^my/new$', 'web.nodes.views.node_new', name = 'new_node'),
  url(r'^nodes/new$', lambda request: redirect('new_node', permanent=True)), # Legacy
  url(r'^my/whitelist$', 'web.nodes.views.whitelisted_mac', name = 'my_whitelist'),
  url(r'^nodes/whitelisted_mac$', lambda request: redirect('my_whitelist', permanent=True)), # Legacy
  url(r'^my/whitelist/remove/(?P<item_id>\d+)$', 'web.nodes.views.unwhitelist_mac', name = 'my_whitelist_remove'),  
  url(r'^my/events$', 'web.nodes.views.event_list', name = 'my_events'),
  url(r'^my/events/subscribe', 'web.nodes.views.event_subscribe', name = 'my_events_subscribe'),
  url(r'^my/events/unsubscribe/(?P<subscription_id>\d+)$', 'web.nodes.views.event_unsubscribe', name = 'my_events_unsubscribe'),
  url(r'^my/sticker$', 'web.nodes.views.sticker', name = 'my_sticker'),
  url(r'^nodes/sticker$', lambda request: redirect('my_sticker', permanent=True)), # Legacy
  
  # Node itself
  url(r'^node/(?P<node>[^/]+)$', 'web.nodes.views.node', name = 'view_node'),
  url(r'^nodes/node/(?P<node>.*)$', lambda request, node: redirect('view_node', permanent=True, node=node)), # Legacy
  url(r'^node/(?P<node>[^/]+)/events$', 'web.nodes.views.node_events', name = 'view_node_events'),
  url(r'^nodes/events/(?P<node>.*)$', lambda request, node: redirect('view_node_events', permanent=True, node=node)), # Legacy
  url(r'^node/(?P<node>[^/]+)/packages$', 'web.nodes.views.package_list', name = 'view_node_packages'),
  url(r'^nodes/installed_packages/(?P<node>.*)$', lambda request, node: redirect('view_node_packages', permanent=True, node=node)), # Legacy
  
  # Node manipulation
  url(r'^node/(?P<node>[^/]+)/edit$', 'web.nodes.views.node_edit', name = 'edit_node'),
  url(r'^node/(?P<node>[^/]+)/remove$', 'web.nodes.views.node_remove', name = 'remove_node'),
  url(r'^node/(?P<node>[^/]+)/reset$', 'web.nodes.views.node_reset', name = 'reset_node'),
  url(r'^node/(?P<node>[^/]+)/renumber$', 'web.nodes.views.node_renumber', name = 'renumber_node'),
  url(r'^node/(?P<node>[^/]+)/subnet/allocate$', 'web.nodes.views.node_allocate_subnet', name = 'allocate_subnet'),
  url(r'^node/(?P<node>[^/]+)/subnet/(?P<subnet_id>\d+)/deallocate$', 'web.nodes.views.node_deallocate_subnet', name = 'remove_subnet'),
  url(r'^node/(?P<node>[^/]+)/subnet/(?P<subnet_id>\d+)/edit', 'web.nodes.views.node_edit_subnet', name = 'edit_subnet'),
  
  # Feeds
  url(r'^feeds/whitelist$', 'web.nodes.views.whitelist'),
  url(r'^feeds/rss/(?P<url>.*)$', 'django.contrib.syndication.views.feed', { 'feed_dict' : feeds }),

  # Pools
  url(r'^pools$', 'web.nodes.views.pools'),
  url(r'^pools/txt$', 'web.nodes.views.pools_text'),

  # Sitemap
  url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps' : sitemaps }),

  # Generator
  url(r'^generator/request/(?P<node>.*)$', 'web.generator.views.request', name = 'generate_node'),

  # Authentication
  url(r'^auth/login$', 'django.contrib.auth.views.login', {'template_name' : 'auth/login.html'}, name = 'auth_login'),
  url(r'^auth/logout$', 'django.contrib.auth.views.logout_then_login', name = 'auth_logout'),
  url(r'^auth/$', lambda request: redirect('auth_login', permanent=True)),
)

if getattr(settings, 'DEBUG', None):
  urlpatterns += patterns('',
    url(r'^(?P<path>(common|css|graphs|images|js|site|stickers)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
  )
