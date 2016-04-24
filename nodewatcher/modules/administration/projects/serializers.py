from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers

from . import models


class ProjectSerializer(api_serializers.JSONLDSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'name', 'description', 'is_default', 'location')
        base_view = 'apiv2:project-list'

api_serializers.pool.register(ProjectSerializer)
