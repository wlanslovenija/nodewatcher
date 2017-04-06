from rest_framework import serializers

from . import models


class UserAuthenticationKeySerializer(serializers.ModelSerializer):
    """
    Serializer for user authentication keys.
    """

    class Meta:
        model = models.UserAuthenticationKey
        fields = ('id', 'name', 'fingerprint', 'public_key', 'created')
