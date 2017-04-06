from rest_framework import serializers

from . import models


class UnknownNodeSerializer(serializers.ModelSerializer):
    """
    Serializer for unknown nodes.
    """

    class Meta:
        model = models.UnknownNode
        fields = ('uuid', 'first_seen', 'last_seen', 'ip_address', 'certificate', 'origin')
