from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers

from . import models


class BabelTopologyLinkSerializer(api_serializers.JSONLDSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.BabelTopologyLink
        fields = ('id', 'interface', 'rxcost', 'txcost', 'rtt', 'rttcost', 'cost', 'reachability')

api_serializers.pool.register(BabelTopologyLinkSerializer)
