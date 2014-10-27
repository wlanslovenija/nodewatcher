from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class MapComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^map/$',
            'view': views.Map.as_view(),
            'name': 'map',
        }

components.pool.register(MapComponent)


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Map"),
    url=urlresolvers.reverse_lazy('MapComponent:map'),
))

components.partials.register(components.Partial('map_partial'))
