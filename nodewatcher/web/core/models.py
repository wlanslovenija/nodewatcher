from django import forms
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext as _

from registry import fields as registry_fields
from registry import forms as registry_forms
from registry import registration

class GeneralConfig(registration.bases.NodeConfigRegistryItem):
  """
  General node configuration containing basic parameters about the
  router type and the platform used.
  """
  name = models.CharField(max_length = 30)
  project = registry_fields.ModelSelectorKeyField("nodes.Project")
  location = models.CharField(max_length = 100)
  geolocation = gis_models.PointField()
  altitude = models.IntegerField(default = 0)
  
  class RegistryMeta:
    form_order = 1
    registry_id = "core.general"
    registry_section = _("General Configuration")
    registry_name = _("Basic Configuration")
    lookup_proxies = []

class GeneralConfigForm(forms.ModelForm):
  """
  General configuration form.
  """
  class Meta:
    model = GeneralConfig

registration.point("node.config").register_item(GeneralConfig)
registration.register_form_for_item(GeneralConfig, GeneralConfigForm)

