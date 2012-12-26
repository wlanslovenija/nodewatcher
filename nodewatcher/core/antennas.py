from django.forms import models as model_forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import datastructures

from nodewatcher.registry import fields as registry_fields

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

ANTENNA_FORM_FIELD_PREFIX = 'antenna_'

def save_mixin_decorator(f):
    """
    Augments the save method to install a hook just before the save method
    is called.
    """
    def save(self, *args, **kwargs):
        self._save_antenna_referencer_mixin()
        if f is not None:
            f(self, *args, **kwargs)
        else:
            super(self.__class__, self).save(*args, **kwargs)

    return save

class AntennaReferencerFormMixinMeta(model_forms.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        if name == 'AntennaReferencerFormMixin':
            return type.__new__(cls, name, bases, attrs)

        # Prepare fields for our model
        fields = datastructures.SortedDict()
        for name, field in model_forms.fields_for_model(Antenna).items():
            fields['%s%s' % (ANTENNA_FORM_FIELD_PREFIX, name)] = field
        attrs['_antenna_fields'] = fields

        # Mixin our save method
        attrs['save'] = save_mixin_decorator(attrs.get('save', None))
        return type.__new__(cls, name, bases, attrs)

class AntennaReferencerFormMixin(object):
    """
    A mixin for forms that would like to display antenna selection.
    """
    __metaclass__ = AntennaReferencerFormMixinMeta

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically displays fields for entering new antenna information.
        """
        self.fields['antenna'].empty_label = _("[Add new antenna]")
        try:
            qs = self.fields['antenna'].queryset
            qs = qs.filter(models.Q(internal_for = cfg['core.general'][0].router) | models.Q(internal_for = None))
            qs = qs.order_by("internal_for", "internal_id", "name")
            self.fields['antenna'].queryset = qs
        except (IndexError, KeyError, AttributeError):
            pass

        try:
            if item.antenna is not None:
                self._creating_antenna = False
                return
        except Antenna.DoesNotExist:
            pass

        # Generate fields for entering a new antenna
        self.fields.update(self._antenna_fields)
        self._creating_antenna = True
        self.fields['antenna'].required = False

    def _save_antenna_referencer_mixin(self):
        """
        Creates a new antenna descriptor instance and saves it into the model.
        """
        if not self._creating_antenna:
            return

        # Prepare just the prefixed fields
        orig_cleaned_data = self.cleaned_data
        self.cleaned_data = {}
        for key, value in orig_cleaned_data.items():
            if key.startswith(ANTENNA_FORM_FIELD_PREFIX):
                self.cleaned_data[key[len(ANTENNA_FORM_FIELD_PREFIX):]] = value

        # Create and save the new antenna instance
        antenna = Antenna()
        model_forms.save_instance(self, antenna, fail_message = 'created')
        self.cleaned_data = orig_cleaned_data
        self.instance.antenna = antenna
