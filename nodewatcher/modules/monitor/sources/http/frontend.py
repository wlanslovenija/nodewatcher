from django.conf import urls

from nodewatcher.core.frontend import components

from . import views


class HttpPushComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(HttpPushComponent, cls).get_urls() + [
            # Push endpoint.
            urls.url(r'^push/http/(?P<uuid>.+)/?$', views.HttpPushEndpoint.as_view(), name='endpoint'),
        ]

components.pool.register(HttpPushComponent)
