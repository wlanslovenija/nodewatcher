from django.conf import settings, urls

urlpatterns = urls.patterns('',
    # Node lists
    urls.url(r'^$', 'nodewatcher.legacy.nodes.views.nodes', name = 'nodes_list'),

    # Node maintainers
    urls.url(r'^my/new$', 'nodewatcher.legacy.nodes.views.node_new', name = 'new_node'),

    # Node itself, public
    # (Those views should have permalinks defined and are also those which have be_robust set to True)
    urls.url(r'^node/(?P<node>[^/]+)$', 'nodewatcher.legacy.nodes.views.node_display', name = 'view_node'),

    # Node manipulation
    urls.url(r'^node/(?P<node>[^/]+)/edit$', 'nodewatcher.legacy.nodes.views.node_edit', name = 'edit_node'),

    # Registry
    urls.url(r'^registry/', urls.include('nodewatcher.registry.urls', namespace = 'registry')),

    # Accounts
    urls.url(r'account/', urls.include('nodewatcher.contrib.account.urls')),
    urls.url(r'^user/(?P<username>[\w.@+-]+)/$', 'nodewatcher.contrib.account.views.user', name = 'user_page'),
)

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
if getattr(settings, 'DEBUG', False):
    urlpatterns += urls.patterns('',
        (r'^404/$', handler404),
        (r'^500/$', handler500),
    )

if getattr(settings, 'DEBUG', None) and not settings.MEDIA_URL.startswith('http'):
    # Server static files with Django when running in debug mode and MEDIA_URL is local
    static_patterns = urls.patterns('',
        urls.url(
            r'^(?P<path>(?:common|css|graphs|images|js|site|stickers|wlanlj|wlansi)/.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
        ),
    )

    media_url = settings.MEDIA_URL.lstrip('/')
    urlpatterns += urls.patterns('',
        (r'^%s' % media_url, urls.include(static_patterns)),
    )
