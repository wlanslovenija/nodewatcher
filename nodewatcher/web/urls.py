from django.conf.urls.defaults import *
from web.nodes.feeds import LatestEvents, ActiveNodes
from web.nodes.sitemaps import NodeSitemap, StaticSitemap, RootPageSitemap
from django.conf import settings

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
  # Nodes
  url(r'^$', 'web.nodes.views.nodes'),
  url(r'^nodes/node_list$', 'web.nodes.views.nodes'),
  url(r'^nodes/my_nodes$', 'web.nodes.views.my_nodes', name = 'my_nodes'),
  url(r'^nodes/new$', 'web.nodes.views.node_new', name = 'new_node'),
  url(r'^node/(?P<node>.*?)$', 'web.nodes.views.node'),
  url(r'^nodes/node/(?P<node>.*?)$', 'web.nodes.views.node', name = 'view_node'),
  url(r'^nodes/remove/(?P<node>.*?)$', 'web.nodes.views.node_remove', name = 'remove_node'),
  url(r'^nodes/reset/(?P<node>.*?)$', 'web.nodes.views.node_reset', name = 'reset_node'),
  url(r'^nodes/edit/(?P<node>.*?)$', 'web.nodes.views.node_edit', name = 'edit_node'),
  url(r'^nodes/renumber/(?P<node>.*?)$', 'web.nodes.views.node_renumber', name = 'renumber_node'),
  url(r'^nodes/allocate_subnet/(?P<node>.*?)$', 'web.nodes.views.node_allocate_subnet', name = 'allocate_subnet'),
  url(r'^nodes/deallocate_subnet/(?P<subnet_id>\d+)$', 'web.nodes.views.node_deallocate_subnet', name = 'remove_subnet'),
  url(r'^nodes/edit_subnet/(?P<subnet_id>\d+)$', 'web.nodes.views.node_edit_subnet', name = 'edit_subnet'),
  url(r'^nodes/whitelisted_mac$', 'web.nodes.views.whitelisted_mac'),
  url(r'^nodes/unwhitelist_mac/(?P<item_id>\d+)$', 'web.nodes.views.unwhitelist_mac'),
  url(r'^nodes/gcl$', 'web.nodes.views.gcl'),
  url(r'^nodes/topology$', 'web.nodes.views.topology'),
  url(r'^nodes/map$', 'web.nodes.views.map'),
  url(r'^nodes/sticker$', 'web.nodes.views.sticker'),
  url(r'^nodes/events$', 'web.nodes.views.event_list'),
  url(r'^nodes/events/global$', 'web.nodes.views.global_events'),
  url(r'^nodes/events/(?P<node>.*?)$', 'web.nodes.views.node_events', name = 'view_node_events'),
  url(r'^nodes/event_subscribe', 'web.nodes.views.event_subscribe'),
  url(r'^nodes/event_unsubscribe/(?P<subscription_id>\d+)$', 'web.nodes.views.event_unsubscribe'),
  url(r'^nodes/installed_packages/(?P<node>.*?)$', 'web.nodes.views.package_list', name = 'view_node_packages'),
  url(r'^nodes/statistics$', 'web.nodes.views.statistics'),
  url(r'^feeds/whitelist$', 'web.nodes.views.whitelist'),
  url(r'^feeds/rss/(?P<url>.*)$', 'django.contrib.syndication.views.feed', { 'feed_dict' : feeds }),

  # Pools
  url(r'^ip_pools$', 'web.nodes.views.pools'),
  url(r'^ip_pools/txt$', 'web.nodes.views.pools_text'),

  # Sitemap
  url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps' : sitemaps }),

  # Generator
  url(r'^generator/request/(?P<node>.*?)$', 'web.generator.views.request', name = 'generate_node'),

  # Authentication
  url(r'^auth/(?:login)?$', 'django.contrib.auth.views.login', {'template_name' : 'auth/login.html'}),
  url(r'^auth/logout$', 'django.contrib.auth.views.logout_then_login'),
)

if getattr(settings, 'DEBUG', None):
  urlpatterns += patterns('',
    url(r'^(?P<path>(common|css|graphs|images|js|site|stickers)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
  )
