from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import fields as registry_fields, registration


class Antenna(models.Model):
    """
    Antenna descriptor.
    """

    POLARIZATION_CHOICES = (
        ('horizontal', _("Horizontal")),
        ('vertical', _("Vertical")),
        ('circular', _("Circular")),
        ('dual', _("Dual")),
    )

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    manufacturer = models.CharField(max_length=100, verbose_name=_("Manufacturer"))
    internal_for = models.CharField(max_length=100, editable=False, null=True)
    internal_id = models.CharField(max_length=100, editable=False, null=True)
    url = models.URLField(verbose_name=_("URL"), blank=True)
    polarization = models.CharField(max_length=20, choices=POLARIZATION_CHOICES)
    angle_horizontal = models.IntegerField(default=360, verbose_name=_("Horizontal angle"))
    angle_vertical = models.IntegerField(default=360, verbose_name=_("Vertical angle"))
    gain = models.IntegerField(verbose_name=_("Gain (dBi)"))

    def __unicode__(self):
        """
        Returns a string representation of this model.
        """

        if self.internal_for is not None:
            return _("[%s internal antenna]") % self.internal_for
        else:
            return "%s :: %s" % (self.manufacturer, self.name)


class AntennaEquipmentConfig(registration.bases.NodeConfigRegistryItem):
    """
    Antenna that can be added to a wireless radio.
    """

    device = registry_fields.IntraRegistryForeignKey(
        cgm_models.WifiRadioDeviceConfig, editable=False, null=False, related_name='antennas'
    )
    antenna = registry_fields.ModelSelectorKeyField(Antenna)
    azimuth = models.FloatField(null=True, blank=True)
    elevation_angle = models.FloatField(null=True, blank=True)
    rotation = models.FloatField(null=True, blank=True)

    class RegistryMeta:
        form_weight = 50
        registry_id = 'core.equipment.antenna'
        registry_section = _("Antennas")
        registry_name = _("Antenna")
        multiple = True

registration.point('node.config').register_subitem(cgm_models.WifiRadioDeviceConfig, AntennaEquipmentConfig)
