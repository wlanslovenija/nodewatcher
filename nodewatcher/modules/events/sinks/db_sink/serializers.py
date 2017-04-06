from rest_framework import serializers

from nodewatcher.core import models as core_models
from nodewatcher.core.api import serializers as api_serializers

from . import models


class EventSerializer(object):
    def get_fields(self):
        """
        Add serializer for related node field.
        """

        fields = super(EventSerializer, self).get_fields()
        fields['related_nodes'] = api_serializers.pool.get_serializer(core_models.Node)(
            many=True,
            context=self.context
        )
        return fields


class NodeEventSerializer(EventSerializer, serializers.ModelSerializer):
    """
    Serializer for node events.
    """

    description = serializers.CharField()

    class Meta:
        model = models.SerializedNodeEvent
        fields = ('severity', 'source_name', 'source_type', 'record', 'timestamp',
                  'related_users', 'description')


class NodeWarningSerializer(EventSerializer, serializers.ModelSerializer):
    """
    Serializer for node warnings.
    """

    class Meta:
        model = models.SerializedNodeWarning
        fields = ('uuid', 'severity', 'source_name', 'source_type', 'record',
                  'first_seen', 'last_seen')
