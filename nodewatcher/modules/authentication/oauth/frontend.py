from django.conf import urls

from nodewatcher.core.frontend import components


class OAuthComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(OAuthComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^oauth/', urls.include('oauth2_provider.urls', namespace='oauth2_provider')),
        )

components.pool.register(OAuthComponent)
