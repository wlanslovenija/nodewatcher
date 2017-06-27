from django.core import urlresolvers

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import components

from . import views


class IpSpaceCompontent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/ip_space/$',
            'view': views.IpSpace.as_view(),
            'name': 'IpSpace',
        }

components.pool.register(IpSpaceCompontent)


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Ip space"),
    url=urlresolvers.reverse_lazy('IpSpaceCompontent:IpSpace'),
))


components.partials.register(components.Partial('ip_space_partial'))


components.partials.get_partial('ip_space_partial').add(components.PartialEntry(
    name='general',
    template='network/ip_space/general.html',
    weight=-1
))
