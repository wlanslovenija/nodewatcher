from django.conf import urls

urlpatterns = urls.patterns('',
    # Registry
    urls.url(r'^registry/', urls.include('nodewatcher.registry.urls', namespace = 'registry')),

    # Accounts
    urls.url(r'account/', urls.include('nodewatcher.contrib.account.urls')),
    urls.url(r'^user/(?P<username>[\w.@+-]+)/$', 'nodewatcher.contrib.account.views.user', name = 'user_page'),

    # Frontend
    urls.url(r'^', urls.include('nodewatcher.core.frontend.urls')),
)
