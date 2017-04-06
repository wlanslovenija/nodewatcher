from rest_framework import serializers

from nodewatcher.core import models as core_models
from nodewatcher.core.api import serializers as api_serializers
from nodewatcher.core.generator import models


class BuildChannelSerializer(serializers.ModelSerializer):
    """
    Serializer for build channels.
    """

    class Meta:
        model = models.BuildChannel
        fields = ('name', 'description', 'default')


class BuildVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for build versions.
    """

    class Meta:
        model = models.BuildVersion
        fields = ('name',)


class BuilderSerializer(serializers.ModelSerializer):
    """
    Serializer for builders.
    """

    version = BuildVersionSerializer()

    class Meta:
        model = models.Builder
        fields = ('platform', 'architecture', 'version')


class BuildResultFileSerializer(serializers.ModelSerializer):
    """
    Serializer for build result files.
    """

    class Meta:
        model = models.BuildResultFile
        fields = ('file', 'checksum_md5', 'checksum_sha256')


class BuildResultSerializer(serializers.ModelSerializer):
    """
    Serializer for build results.
    """

    build_channel = BuildChannelSerializer()
    builder = BuilderSerializer()
    files = BuildResultFileSerializer(many=True)

    class Meta:
        model = models.BuildResult
        fields = ('uuid', 'build_channel', 'builder', 'status', 'created', 'last_modified',
                  'files', 'build_log', 'config')

    def get_fields(self):
        """
        Add serializer for node field.
        """

        fields = super(BuildResultSerializer, self).get_fields()
        fields['node'] = api_serializers.pool.get_serializer(core_models.Node)(context=self.context)
        return fields
