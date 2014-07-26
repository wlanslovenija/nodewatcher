from django.core import urlresolvers

from nodewatcher.core.frontend import api, components

from . import resources, views


class EventsComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/events/$',
            'view': views.EventsList.as_view(),
            'name': 'events',
        }

components.pool.register(EventsComponent)


api.v1_api.register(resources.EventResource())


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Events"),
    url=urlresolvers.reverse_lazy('EventsComponent:events'),
))
