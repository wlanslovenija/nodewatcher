from nodewatcher.core.frontend import components

from . import views

class ListComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^list/$',
            'view': views.NodesList.as_view(),
            'name': 'list',
        }

components.pool.register(ListComponent)