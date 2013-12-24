from django.conf import urls

from nodewatcher.core.frontend import components


class AccountComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(AccountComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'account/', urls.include('nodewatcher.extra.account.urls')),
            urls.url(r'^user/(?P<username>[\w.@+-]+)/$', 'nodewatcher.extra.account.views.user', name='user_page'),
        )

components.pool.register(AccountComponent)
