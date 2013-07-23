from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.frontend import components
from nodewatcher.core.frontend.components import exceptions

from . import views


class EditorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(EditorComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^my/new/$', views.NewNode.as_view(), name='new'),
            urls.url(r'^node/(?P<pk>[^/]+)/edit/$', views.EditNode.as_view(), name='edit'),
        )

components.pool.register(EditorComponent)

try:
    components.menus.get_menu('display_node_menu').add(components.MenuEntry(
        label=components.ugettext_lazy("Edit node"),
        url=lambda context: urlresolvers.reverse('editor:edit', context['node'].pk),
    ))
except exceptions.MenuNotRegistered:
    pass
