from django.conf import urls

from nodewatcher.core.frontend import components

from . import views

class EditorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(EditorComponent, cls).get_urls() + urls.patterns('',
            urls.url(r'^my/new/$', views.NewNode.as_view(), name='new'),
            urls.url(r'^node/(?P<node>[^/]+)/edit/$', views.EditNode.as_view(), name='edit'),
        )

components.pool.register(EditorComponent)