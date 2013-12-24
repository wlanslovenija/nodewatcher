from django.conf import urls

from nodewatcher.core.frontend import components


class DatastreamComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(DatastreamComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^api/', urls.include('django_datastream.urls')),
        )

components.pool.register(DatastreamComponent)
