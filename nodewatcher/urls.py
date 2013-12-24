from django.conf import settings, urls
from django.conf.urls import static

urlpatterns = urls.patterns(
    '',

    # Registry
    urls.url(r'^registry/', urls.include('nodewatcher.core.registry.urls', namespace='registry', app_name='registry')),

    # Frontend
    urls.url(r'^', urls.include('nodewatcher.core.frontend.urls')),
)

# See CSRF_FAILURE_VIEW in settings.py as well
handler403 = 'missing.views.forbidden_view'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

if settings.DEBUG:
    urlpatterns += urls.patterns(
        '',

        (r'^403/$', handler403),
        (r'^404/$', handler404),
        (r'^500/$', handler500),
    )

if settings.DEBUG:
    # Serve static files in DEBUG mode
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
