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
  (r'^$', 'wlanlj.nodes.views.nodes'),
  (r'^nodes/node_list$', 'wlanlj.nodes.views.nodes'),
  (r'^nodes/my_nodes$', 'wlanlj.nodes.views.my_nodes'),
  (r'^nodes/new$', 'wlanlj.nodes.views.node_new'),
  (r'^nodes/node/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.node'),
  (r'^nodes/remove/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.node_remove'),
  (r'^nodes/reset/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.node_reset'),
  (r'^nodes/edit/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.node_edit'),
  (r'^nodes/allocate_subnet/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.node_allocate_subnet'),
  (r'^nodes/deallocate_subnet/(?P<subnet_id>\d+)$', 'wlanlj.nodes.views.node_deallocate_subnet'),
  (r'^nodes/whitelisted_mac$', 'wlanlj.nodes.views.whitelisted_mac'),
  (r'^nodes/unwhitelist_mac/(?P<item_id>\d+)$', 'wlanlj.nodes.views.unwhitelist_mac'),
  (r'^nodes/gcl$', 'wlanlj.nodes.views.gcl'),
  (r'^nodes/topology$', 'wlanlj.nodes.views.topology'),
  (r'^nodes/map$', 'wlanlj.nodes.views.map'),
  (r'^nodes/sticker$', 'wlanlj.nodes.views.sticker'),
  (r'^nodes/events$', 'wlanlj.nodes.views.event_list'),
  (r'^nodes/events/global$', 'wlanlj.nodes.views.global_events'),
  (r'^nodes/event_subscribe', 'wlanlj.nodes.views.event_subscribe'),
  (r'^nodes/event_unsubscribe/(?P<subscription_id>\d+)$', 'wlanlj.nodes.views.event_unsubscribe'),
  (r'^nodes/installed_packages/(?P<node_ip>.*?)$', 'wlanlj.nodes.views.package_list'),
  (r'^nodes/statistics$', 'wlanlj.nodes.views.statistics'),
  (r'^feeds/whitelist$', 'wlanlj.nodes.views.whitelist'),
  (r'^feeds/rss/(?P<url>.*)$', 'django.contrib.syndication.views.feed', { 'feed_dict' : feeds }),

  # Pools
  (r'^ip_pools$', 'wlanlj.nodes.views.pools'),
  (r'^ip_pools/txt$', 'wlanlj.nodes.views.pools_text'),

  # Sitemap
  (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', { 'sitemaps' : sitemaps }),

  # Generator
  (r'^generator/request/(?P<node_ip>.*?)$', 'wlanlj.generator.views.request'),

  # Authentication
  (r'^auth/(?:login)?$', 'django.contrib.auth.views.login',
   {'template_name' : 'auth/login.html'}),

  (r'^auth/logout$', 'django.contrib.auth.views.logout_then_login'),
)

if settings.DEBUG or True:
  urlpatterns += patterns('',
    (r'^(?P<path>(css|graphs|images|js|results|stickers)/.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
  )
