from django.forms import models as model_forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import datastructures

from web.registry import fields as registry_fields

class Antenna(models.Model):
  """
  Antenna descriptor.
  """
  POLARIZATION_CHOICES = (
    ('horizontal', _("Horizontal")),
    ('vertical', _("Vertical")),
  )
  
  name = models.CharField(max_length = 100, verbose_name = _("Name"))
  manufacturer = models.CharField(max_length = 100, verbose_name = _("Manufacturer"))
  url = models.URLField(verify_exists = False, verbose_name = _("URL"), blank = True)
  polarization = models.CharField(max_length = 20, choices = POLARIZATION_CHOICES)
  angle_horizontal = models.IntegerField(default = 360, verbose_name = _("Horizontal angle"))
  angle_vertical = models.IntegerField(default = 360, verbose_name = _("Vertical angle"))
  gain = models.IntegerField(verbose_name = _("Gain (dBi)"))
  
  class Meta:
    app_label = "core"
  
  def __unicode__(self):
    return "%s - %s" % (self.manufacturer, self.name)

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
  
  def modify_to_context(self, item, cfg):
    """
    Dynamically displays fields for entering new antenna information.
    """
    self.fields['antenna'].empty_label = _("[Add new antenna]")
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
    print orig_cleaned_data
    print self.cleaned_data
    model_forms.save_instance(self, antenna, fail_message = 'created')
    self.cleaned_data = orig_cleaned_data
    self.instance.antenna = antenna

