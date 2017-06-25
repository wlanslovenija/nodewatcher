from django.core import urlresolvers

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import components

from . import views


class CidrCompontent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/cidr/$',
            'view': views.Cidr.as_view(),
            'name': 'cidr',
        }

components.pool.register(CidrCompontent)


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Cidr map"),
    url=urlresolvers.reverse_lazy('CidrCompontent:cidr'),
))


components.partials.register(components.Partial('cidr_partial'))


components.partials.get_partial('cidr_partial').add(components.PartialEntry(
    name='general',
    template='network/statistics/general.html',
    weight=-1,
    extra_context=lambda context: {
        'count': core_models.Node.objects.count(),
    },
))
