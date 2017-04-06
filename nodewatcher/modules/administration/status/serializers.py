from rest_framework import serializers

from nodewatcher.core.registry.api import serializers as registry_serializers


class StatusStatisticsSerializer(serializers.Serializer):
    """
    Serializer for global per-status statistics.
    """

    status = registry_serializers.RegisteredChoiceSerializer(
        regpoint='node.monitoring',
        choices='core.status#network'
    )
    nodes = serializers.IntegerField()
