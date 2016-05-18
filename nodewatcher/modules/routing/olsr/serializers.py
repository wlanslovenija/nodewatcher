from rest_framework import serializers

from nodewatcher.core.api import serializers as api_serializers

from . import models


class OlsrTopologyLinkSerializer(api_serializers.JSONLDSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.OlsrTopologyLink
        fields = ('id', 'lq', 'ilq', 'etx')

api_serializers.pool.register(OlsrTopologyLinkSerializer)
