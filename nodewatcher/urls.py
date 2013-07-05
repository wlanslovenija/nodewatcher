from django.conf import settings, urls
from django.conf.urls import static

urlpatterns = urls.patterns('',
    # Registry
    urls.url(r'^registry/', urls.include('nodewatcher.core.registry.urls', namespace='registry')),

    # Accounts
    urls.url(r'account/', urls.include('nodewatcher.extra.account.urls')),
    urls.url(r'^user/(?P<username>[\w.@+-]+)/$', 'nodewatcher.extra.account.views.user', name='user_page'),

    # Frontend
    urls.url(r'^', urls.include('nodewatcher.core.frontend.urls')),
)

if settings.DEBUG:
    # Serve static files in DEBUG mode
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
