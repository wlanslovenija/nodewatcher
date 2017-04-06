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

    def get_fields(self):
        """
        Add serializer for peer field.
        """

        fields = super(TopologyLinkSerializer, self).get_fields()
        fields['peer'] = api_serializers.pool.get_serializer(core_models.Node)(context=self.context)
        return fields
