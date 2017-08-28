import datetime

from django.db import models as django_models
from django.utils import timezone

from rest_framework import mixins, viewsets

from nodewatcher.core import models as core_models

from . import serializers


class StatusStatisticsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Endpoint for global per-status statistics.
    """

    queryset = core_models.Node.objects.regpoint('monitoring').registry_fields(
        status='core.status__network'
    ).regpoint('monitoring').registry_filter(
        # Ignore nodes, which haven't been seen for more than 180 days.
        core_general__last_seen__gt=timezone.now() - datetime.timedelta(days=180),
    ).values(
        'status'
    ).annotate(
        nodes=django_models.Count('uuid')
    )
    serializer_class = serializers.StatusStatisticsSerializer
