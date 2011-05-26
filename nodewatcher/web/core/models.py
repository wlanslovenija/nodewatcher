from django import forms
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext as _

from web.core import allocation
from web.registry import fields as registry_fields
from web.registry import forms as registry_form
from web.registry import registration
from web.registry import widgets as registry_widgets

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
    widgets = {
      'geolocation' : registry_widgets.LocationWidget(
        map_width = 400,
        map_height = 300
      )
    }
  
  def modify_to_context(self, item, cfg):
    """
    Dynamically modifies the form.
    """
    # Update the location widget's coordinates accoording to project
    if item.project:
      self.fields['geolocation'].widget.default_location = [
        item.project.geo_lat,
        item.project.geo_long,
        item.project.geo_zoom
      ]

registration.point("node.config").register_item(GeneralConfig)
registration.register_form_for_item(GeneralConfig, GeneralConfigForm)

class BasicAddressingConfig(registration.bases.NodeConfigRegistryItem, allocation.AddressAllocator):
  """
  Enables allocation of subnets for the node without the need to define any interfaces.
  """
  class RegistryMeta:
    form_order = 51
    registry_id = "core.basic-addressing"
    registry_section = _("Subnet Allocation")
    registry_name = _("Subnet")
    multiple = True

class BasicAddressingConfigForm(forms.ModelForm, allocation.AddressAllocatorFormMixin):
  """
  General configuration form.
  """
  class Meta:
    model = BasicAddressingConfig

registration.point("node.config").register_item(BasicAddressingConfig)
registration.register_form_for_item(BasicAddressingConfig, BasicAddressingConfigForm)

