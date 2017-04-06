from django.db import models as django_models

from rest_framework import mixins, viewsets

from nodewatcher.core import models as core_models

from . import serializers


class DeviceStatisticsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Endpoint for global per-device statistics.
    """

    queryset = core_models.Node.objects.regpoint('config').registry_fields(
        device='core.general__router'
    ).values(
        'device'
    ).annotate(
        nodes=django_models.Count('uuid')
    )
    serializer_class = serializers.DeviceStatisticsSerializer
