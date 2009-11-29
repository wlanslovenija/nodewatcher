from django.conf.urls.defaults import *
from wlanlj.nodes.feeds import LatestEvents
from wlanlj.nodes.sitemaps import NodeSitemap, StaticSitemap
from django.conf import settings

feeds = {
  'events'  : LatestEvents
}

sitemaps = {
  'nodes'   : NodeSitemap,
  'static'  : StaticSitemap
}

urlpatterns = patterns('',
  # Nodes
  url(r'^$', 'wlanlj.nodes.views.nodes'),
  url(r'^nodes/node_list$', 'wlanlj.nodes.views.nodes'),
  url(r'^nodes/my_nodes$', 'wlanlj.nodes.views.my_nodes', name = 'my_nodes'),
  url(r'^nodes/new$', 'wlanlj.nodes.views.node_new', name = 'new_node'),
  url(r'^node/(?P<node>.*?)$', 'wlanlj.nodes.views.node'),
  url(r'^nodes/node/(?P<node>.*?)$', 'wlanlj.nodes.views.node', name = 'view_node'),
  url(r'^nodes/remove/(?P<node>.*?)$', 'wlanlj.nodes.views.node_remove', name = 'remove_node'),
  url(r'^nodes/reset/(?P<node>.*?)$', 'wlanlj.nodes.views.node_reset', name = 'reset_node'),
  url(r'^nodes/edit/(?P<node>.*?)$', 'wlanlj.nodes.views.node_edit', name = 'edit_node'),
  url(r'^nodes/renumber/(?P<node>.*?)$', 'wlanlj.nodes.views.node_renumber', name = 'renumber_node'),
  url(r'^nodes/allocate_subnet/(?P<node>.*?)$', 'wlanlj.nodes.views.node_allocate_subnet', name = 'allocate_subnet'),
  url(r'^nodes/deallocate_subnet/(?P<subnet_id>\d+)$', 'wlanlj.nodes.views.node_deallocate_subnet'),
  url(r'^nodes/whitelisted_mac$', 'wlanlj.nodes.views.whitelisted_mac'),
  url(r'^nodes/unwhitelist_mac/(?P<item_id>\d+)$', 'wlanlj.nodes.views.unwhitelist_mac'),
  url(r'^nodes/gcl$', 'wlanlj.nodes.views.gcl'),
  url(r'^nodes/topology$', 'wlanlj.nodes.views.topology'),
  url(r'^nodes/map$', 'wlanlj.nodes.views.map'),
  url(r'^nodes/sticker$', 'wlanlj.nodes.views.sticker'),
  url(r'^nodes/events$', 'wlanlj.nodes.views.event_list'),
  url(r'^nodes/events/global$', 'wlanlj.nodes.views.global_events'),
  url(r'^nodes/event_subscribe', 'wlanlj.nodes.views.event_subscribe'),
  url(r'^nodes/event_unsubscribe/(?P<subscription_id>\d+)$', 'wlanlj.nodes.views.event_unsubscribe'),
  url(r'^nodes/installed_packages/(?P<node>.*?)$', 'wlanlj.nodes.views.package_list', name = 'view_node_packages'),
  url(r'^nodes/statistics$', 'wlanlj.nodes.views.statistics'),
  url(r'^feeds/whitelist$', 'wlanlj.nodes.views.whitelist'),
  url(r'^feeds/rss/(?P<url>.*)$', 'django.contrib.syndication.views.feed', { 'feed_dict' : feeds }),

  # Pools
  url(r'^ip_pools$', 'wlanlj.nodes.views.pools'),
  url(r'^ip_pools/txt$', 'wlanlj.nodes.views.pools_text'),

  # Sitemap
  url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps' : sitemaps }),

  # Generator
  url(r'^generator/request/(?P<node>.*?)$', 'wlanlj.generator.views.request', name = 'generate_node'),

  # Authentication
  url(r'^auth/(?:login)?$', 'django.contrib.auth.views.login', {'template_name' : 'auth/login.html'}),
  url(r'^auth/logout$', 'django.contrib.auth.views.logout_then_login'),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^(?P<path>(common|css|graphs|images|js|site|stickers)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
  )
