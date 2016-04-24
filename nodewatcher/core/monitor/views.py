from django.db import models as django_models

from rest_framework import viewsets

from nodewatcher.core import models as core_models
from nodewatcher.core.api import urls as api_urls

from . import models, serializers


class TopologyLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TopologyLink.objects.prefetch_related(
        django_models.Prefetch(
            'peer',
            queryset=core_models.Node.objects.regpoint('config').registry_fields(
                name='core.general__name',
                router_id='core.routerid__router_id',
            )
        ),
    )
    serializer_class = serializers.TopologyLinkSerializer

api_urls.v2_api.register('link', TopologyLinkViewSet)
