import datetime

from django.db import models as django_models
from django.utils import timezone

from rest_framework import mixins, viewsets

from nodewatcher.core import models as core_models

from . import models, serializers


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for project information.
    """

    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class ProjectStatisticsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Endpoint for global per-project statistics.
    """

    queryset = core_models.Node.objects.regpoint('config').registry_fields(
        project='core.project__project__name'
    ).regpoint('monitoring').registry_filter(
        # Ignore nodes, which haven't been seen for more than 180 days.
        core_general__last_seen__gt=timezone.now() - datetime.timedelta(days=180),
    ).values(
        'project'
    ).annotate(
        nodes=django_models.Count('uuid')
    )
    serializer_class = serializers.ProjectStatisticsSerializer
