from rest_framework import serializers

from nodewatcher.core.generator.cgm import base as cgm_base
from nodewatcher.core.registry.api import serializers as registry_serializers


class DeviceChoiceSerializer(registry_serializers.RegisteredChoiceSerializer):
    """
    Device choice serializer.
    """

    manufacturer = serializers.CharField()
    model = serializers.CharField()

    def __init__(self, *args, **kwargs):
        """
        Construct device choice serializer.
        """

        # Ensure all CGMs are loaded so that we get all the device metadata.
        cgm_base.registry.discover()

        kwargs['regpoint'] = 'node.config'
        kwargs['choices'] = 'core.general#router'

        super(DeviceChoiceSerializer, self).__init__(*args, **kwargs)


class DeviceStatisticsSerializer(serializers.Serializer):
    """
    Serializer for global per-device statistics.
    """

    device = DeviceChoiceSerializer()
    nodes = serializers.IntegerField()
