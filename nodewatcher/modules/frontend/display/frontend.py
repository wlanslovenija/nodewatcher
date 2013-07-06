from django.conf import urls

from nodewatcher.core.frontend import components

from . import views

class DisplayComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(DisplayComponent, cls).get_urls() + urls.patterns('',
            urls.url(r'^node/(?P<node>[^/]+)/$', views.DisplayNode.as_view(), name='node'),
        )

components.pool.register(DisplayComponent)