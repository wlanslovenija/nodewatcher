from django.conf import urls

from nodewatcher.core.frontend import components


class AccountsComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(AccountsComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'account/', urls.include('nodewatcher.extra.accounts.urls')),
            urls.url(r'^user/(?P<username>[\w.@+-]+)/$', 'nodewatcher.extra.accounts.views.user', name='user_page'),
        )

components.pool.register(AccountsComponent)
