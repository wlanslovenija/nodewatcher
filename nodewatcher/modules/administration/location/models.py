from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

import timezone_field
from django_countries import fields as country_field

from nodewatcher.core.registry import registration


class LocationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the location of a node.
    """

    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True) # TODO: Autocomplete city field?
    country = country_field.CountryField(null=True, blank=True)
    timezone = timezone_field.TimeZoneField(null=True, blank=True)
    geolocation = gis_models.PointField(null=True, blank=True)
    altitude = models.FloatField(default=0, help_text=_("In meters."))

    geo_objects = gis_models.GeoManager()

    class RegistryMeta:
        form_weight = 3
        registry_id = 'core.location'
        registry_section = _("Location")
        registry_name = _("Basic Location")

registration.point('node.config').register_item(LocationConfig)
