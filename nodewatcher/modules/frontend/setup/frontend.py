from nodewatcher.core.frontend import components

from . import views


class SetupComponent(components.FrontendComponent):
    @classmethod
    def get_main_url(cls):
        return {
            'regex': r'^setup/$',
            'view': views.SetupPage.as_view(),
            'name': 'setup',
        }

components.pool.register(SetupComponent)
