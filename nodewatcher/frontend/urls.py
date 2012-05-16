from django.conf.urls.defaults import *
from django.conf import settings
from django.shortcuts import redirect

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

  # Authentication
  url(r'^auth/login$', 'django.contrib.auth.views.login', { 'template_name' : 'auth/login.html' }, name = 'auth_login'),
  url(r'^auth/logout$', 'django.contrib.auth.views.logout_then_login', name = 'auth_logout'),
  url(r'^auth/$', lambda request: redirect('auth_login', permanent=True)),
)

handler500 = 'frontend.nodes.views.server_error'
if getattr(settings, 'DEBUG', None):
  urlpatterns += patterns('',
    (r'^500/$', 'frontend.nodes.views.server_error'),
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
