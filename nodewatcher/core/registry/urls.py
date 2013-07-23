from django.conf import urls

urlpatterns = urls.patterns(
    'nodewatcher.core.registry.views',
    urls.url(r'evaluate_forms/(?P<regpoint_id>.*)/(?P<root_id>.*)$', 'evaluate_forms', name='evaluate_forms'),
)
