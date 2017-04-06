from django.db import models as django_models

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
    ).values(
        'project'
    ).annotate(
        nodes=django_models.Count('uuid')
    )
    serializer_class = serializers.ProjectStatisticsSerializer
