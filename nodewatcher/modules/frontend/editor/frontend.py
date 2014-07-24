from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class EditorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(EditorComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^node/new/$', views.NewNode.as_view(), name='new'),
            urls.url(r'^node/(?P<pk>[^/]+)/edit/$', views.EditNode.as_view(), name='edit'),
            urls.url(r'^node/(?P<pk>[^/]+)/reset/$', views.ResetNode.as_view(), name='reset'),
            urls.url(r'^node/(?P<pk>[^/]+)/remove/$', views.RemoveNode.as_view(), name='remove'),
        )

components.pool.register(EditorComponent)


components.menus.get_menu('display_node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Edit"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:edit', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('change_node', context['node']),
))

components.menus.get_menu('display_node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Reset"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:reset', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('reset_node', context['node']),
))

components.menus.get_menu('display_node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Remove"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:remove', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('remove_node', context['node']),
))
