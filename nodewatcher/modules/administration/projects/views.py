from rest_framework import viewsets

from nodewatcher.core.api import urls as api_urls

from . import models, serializers


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer

api_urls.v2_api.register('project', ProjectViewSet)
