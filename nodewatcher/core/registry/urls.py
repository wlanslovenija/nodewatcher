from django.conf import urls

from . import views

urlpatterns = [
    urls.url(r'evaluate_forms/(?P<regpoint_id>.*)/(?P<root_id>.*)/$', views.evaluate_forms, name='evaluate_forms'),
]
