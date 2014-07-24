from django.core import urlresolvers

from nodewatcher.core.frontend import api, components

from . import resources, views


class ListComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^list/$',
            'view': views.NodesList.as_view(),
            'name': 'list',
        }

components.pool.register(ListComponent)


api.v1_api.register(resources.NodeResource())


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Node List"),
    url=urlresolvers.reverse_lazy('ListComponent:list'),
))
