from django_datastream import urls

from nodewatcher.core.frontend import api

for resource in urls.v1_api._registry.values():
    api.v1_api.register(resource)
