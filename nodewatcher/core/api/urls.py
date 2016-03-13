from tastypie import api

from rest_framework import routers

# Create v1 API (Tastypie).
v1_api = api.NamespacedApi(api_name='v1', urlconf_namespace='api')

# Create v2 API (Django Rest Framework).
v2_api = routers.DefaultRouter()
