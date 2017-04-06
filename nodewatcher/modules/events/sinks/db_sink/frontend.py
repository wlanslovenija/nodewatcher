from django.core import urlresolvers

from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import components

from . import views


class EventsComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^network/events/$',
            'view': views.EventsList.as_view(),
            'name': 'events',
        }

components.pool.register(EventsComponent)

api_urls.v2_api.register('event', views.EventViewSet)
api_urls.v2_api.register('warning', views.WarningViewSet)

components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Events"),
    url=urlresolvers.reverse_lazy('EventsComponent:events'),
))
