from django.db import models as django_models

from rest_framework import viewsets

from nodewatcher.core import models as core_models
from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.registry import api as registry_api

from . import models, serializers


class TopologyLinkViewSet(registry_api.RegistryRootViewSetMixin,
                          viewsets.ReadOnlyModelViewSet):
    queryset = models.TopologyLink.objects.all()
    serializer_class = serializers.TopologyLinkSerializer
    registry_root_fields = ['peer']

api_urls.v2_api.register('link', TopologyLinkViewSet)
