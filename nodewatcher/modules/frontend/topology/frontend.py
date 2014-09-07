from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class TopologyComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^topology/$',
            'view': views.Topology.as_view(),
            'name': 'topology',
        }

components.pool.register(TopologyComponent)


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Network Topology"),
    url=urlresolvers.reverse_lazy('TopologyComponent:topology'),
))

components.partials.register(components.Partial('network_topology_partial'))
