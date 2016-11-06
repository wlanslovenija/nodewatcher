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

    def get_queryset(self):
        """
        Augments the queryset to allow filtering by node.
        """

        queryset = super(TopologyLinkViewSet, self).get_queryset()
        node = self.request.query_params.get('node', None)
        if node is not None:
            queryset = queryset.filter(monitor__root__pk=node)
        return queryset

api_urls.v2_api.register('link', TopologyLinkViewSet)
