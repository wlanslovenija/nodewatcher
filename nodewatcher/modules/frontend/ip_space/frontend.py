from django.core import urlresolvers
from nodewatcher.core.frontend import components

from . import views


class IpSpaceComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/ip_space/$',
            'view': views.IpSpace.as_view(),
            'name': 'IpSpace',
        }


components.pool.register(IpSpaceComponent)
components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("IP space"),
    url=urlresolvers.reverse_lazy('IpSpaceComponent:IpSpace'),
))
