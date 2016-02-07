from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class EditorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(EditorComponent, cls).get_urls() + [
            urls.url(r'^my/nodes/new/$', views.NewNode.as_view(), name='new'),
            urls.url(r'^node/(?P<pk>[^/]+)/edit/$', views.EditNode.as_view(), name='edit'),
            urls.url(r'^node/(?P<pk>[^/]+)/reset/$', views.ResetNode.as_view(), name='reset'),
            urls.url(r'^node/(?P<pk>[^/]+)/remove/$', views.RemoveNode.as_view(), name='remove'),
        ]

components.pool.register(EditorComponent)


components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Register New Node"),
    url=urlresolvers.reverse_lazy('EditorComponent:new'),
    visible=lambda menu_entry, request, context: request.user.has_perm('core.add_node'),
))

components.menus.get_menu('node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Edit"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:edit', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('core.change_node', context['node']),
))

components.menus.get_menu('node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Reset"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:reset', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('core.reset_node', context['node']),
))

components.menus.get_menu('node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Remove"),
    url=lambda menu_entry, context: urlresolvers.reverse('EditorComponent:remove', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('core.delete_node', context['node']),
))
