from django.core import urlresolvers

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
