from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration

class LocationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the location of a node.
    """

    address = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100) # TODO city field?
    country = models.CharField(max_length = 100) # TODO country field?
    geolocation = gis_models.PointField(null = True)
    altitude = models.FloatField(default = 0)

    class RegistryMeta:
        form_order = 3
        registry_id = 'core.location'
        registry_section = _("Location")
        registry_name = _("Basic Location")

registration.point('node.config').register_item(LocationConfig)
