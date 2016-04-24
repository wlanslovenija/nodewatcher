from rest_framework import serializers

from nodewatcher.core import models as core_models
from nodewatcher.core.api import serializers as api_serializers

from . import models


class TopologyLinkSerializer(api_serializers.PolymorphicSerializerMixin,
                             api_serializers.JSONLDSerializerMixin,
                             serializers.ModelSerializer):
    class Meta:
        model = models.TopologyLink
        fields = ('id', 'last_seen')
        base_view = 'apiv2:topologylink-list'

    def __init__(self, *args, **kwargs):
        super(TopologyLinkSerializer, self).__init__(*args, **kwargs)

        # Add serializer for peer field.
        self.fields['peer'] = api_serializers.pool.get_serializer(core_models.Node)(context=self.context)

api_serializers.pool.register(TopologyLinkSerializer)
