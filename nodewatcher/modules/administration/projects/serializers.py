from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers

from . import models


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project

api_serializers.pool.register(ProjectSerializer)
