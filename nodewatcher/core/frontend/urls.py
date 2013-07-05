from django.conf import settings, urls

urlpatterns = urls.patterns('',
    # Node lists
    urls.url(r'^$', 'nodewatcher.core.frontend.views.nodes', name = 'nodes_list'),

    # Node maintainers
    urls.url(r'^my/new$', 'nodewatcher.core.frontend.views.node_new', name = 'new_node'),

    # Node itself, public
    # (Those views should have permalinks defined and are also those which have be_robust set to True)
    urls.url(r'^node/(?P<node>[^/]+)$', 'nodewatcher.core.frontend.views.node_display', name = 'view_node'),

    # Node manipulation
    urls.url(r'^node/(?P<node>[^/]+)/edit$', 'nodewatcher.core.frontend.views.node_edit', name = 'edit_node'),
)
