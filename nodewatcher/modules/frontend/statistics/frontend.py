import datetime

from django.core import urlresolvers
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import components

from . import views


class NetworkStatisticsComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/statistics/$',
            'view': views.NetworkStatistics.as_view(),
            'name': 'statistics',
        }

components.pool.register(NetworkStatisticsComponent)


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Network Statistics"),
    url=urlresolvers.reverse_lazy('NetworkStatisticsComponent:statistics'),
))


components.partials.register(components.Partial('network_statistics_partial'))


components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='general',
    template='network/statistics/general.html',
    weight=-1,
    extra_context=lambda context: {
        'count': core_models.Node.objects.count(),
        'active': core_models.Node.objects.regpoint('monitoring').registry_filter(
            core_general__last_seen__gt=timezone.now() - datetime.timedelta(days=180),
        ).count(),
    },
))
