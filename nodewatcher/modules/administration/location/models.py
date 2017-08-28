import pytz

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

import timezone_field
from django_countries import fields as country_field
from rest_framework import serializers

from nodewatcher.core.registry import registration, api


class LocationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the location of a node.
    """

    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)  # TODO: Autocomplete city field?
    country = country_field.CountryField(null=True, blank=True)
    timezone = timezone_field.TimeZoneField(null=True, blank=True)
    geolocation = gis_models.PointField(geography=True, null=True, blank=True)
    altitude = models.FloatField(default=0, help_text=_("In meters."))

    class RegistryMeta:
        form_weight = 3
        registry_id = 'core.location'
        registry_section = _("Location")
        registry_name = _("Basic Location")

registration.point('node.config').register_item(LocationConfig)


class TimeZoneField(serializers.Field):
    def to_representation(self, value):
        return value.zone

    def to_internal_value(self, value):
        return pytz.timezone(value)


class LocationConfigSerializer(api.RegistryItemSerializerMixin, serializers.ModelSerializer):
    timezone = TimeZoneField()

    class Meta:
        model = LocationConfig
        fields = '__all__'

registration.register_serializer_for_item(LocationConfig, LocationConfigSerializer)
