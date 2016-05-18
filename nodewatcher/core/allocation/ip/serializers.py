from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers

from . import models


class TopLevelIpPoolSerializer(api_serializers.JSONLDSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.IpPool
        fields = ('id', 'description')
        base_view = 'apiv2:ippool-list'


class IpPoolSerializer(api_serializers.JSONLDSerializerMixin, serializers.ModelSerializer):
    top_level = TopLevelIpPoolSerializer()

    class Meta:
        model = models.IpPool
        fields = ('id', 'family', 'network', 'prefix_length', 'status', 'description',
                  'prefix_length_default', 'prefix_length_minimum', 'prefix_length_maximum',
                  'held_from', 'top_level')
        base_view = 'apiv2:ippool-list'

api_serializers.pool.register(IpPoolSerializer)
