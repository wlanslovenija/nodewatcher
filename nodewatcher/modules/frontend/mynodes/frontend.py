from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class MyNodesComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^my/nodes/$',
            'view': views.MyNodesList.as_view(),
            'name': 'mynodes',
        }

components.pool.register(MyNodesComponent)


components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("My Nodes"),
    url=urlresolvers.reverse_lazy('MyNodesComponent:mynodes'),
    visible=lambda menu_entry, request, context: request.user.is_authenticated(),
))
