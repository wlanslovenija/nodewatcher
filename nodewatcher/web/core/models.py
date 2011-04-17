from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.registry import models as registry_models
from web.registry import forms as registry_forms

class HardwareConfig(registry_models.RegistryItem):
  model = models.CharField(max_length = 20) # TODO fkey to models
  
  class RegistryMeta:
    form_order = 1
    registry_id = "core.hardware"
    registry_name = _("Hardware Configuration")

class HardwareConfigForm(forms.ModelForm):
  class Meta:
    model = HardwareConfig

registry_models.register_form_for_item(HardwareConfig, HardwareConfigForm)

class HardwareFooConfig(HardwareConfig):
  pass

class HardwareFooConfigForm(forms.ModelForm):
  class Meta:
    model = HardwareFooConfig

registry_models.register_form_for_item(HardwareFooConfig, HardwareFooConfigForm)

