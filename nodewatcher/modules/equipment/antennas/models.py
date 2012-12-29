from django.db import models
from django.utils.translation import ugettext_lazy as _

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

    name = models.CharField(max_length = 100, verbose_name = _("Name"))
    manufacturer = models.CharField(max_length = 100, verbose_name = _("Manufacturer"))
    internal_for = models.CharField(max_length = 100, editable = False, null = True)
    internal_id = models.CharField(max_length = 100, editable = False, null = True)
    url = models.URLField(verify_exists = False, verbose_name = _("URL"), blank = True)
    polarization = models.CharField(max_length = 20, choices = POLARIZATION_CHOICES)
    angle_horizontal = models.IntegerField(default = 360, verbose_name = _("Horizontal angle"))
    angle_vertical = models.IntegerField(default = 360, verbose_name = _("Vertical angle"))
    gain = models.IntegerField(verbose_name = _("Gain (dBi)"))

    class Meta:
        app_label = "core"

    def __unicode__(self):
        """
        Returns a string representation of this model.
        """

        if self.internal_for is not None:
            return _("[%s internal antenna]") % self.internal_for
        else:
            return "%s :: %s" % (self.manufacturer, self.name)
