from django import forms
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext as _

from web.core import allocation, antennas
# TODO project model should be moved to core
from web.nodes import models as nodes_models
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
  type = registry_fields.SelectorKeyField("node.config", "core.general#type")
  project = registry_fields.ModelSelectorKeyField("nodes.Project")
  location = models.CharField(max_length = 100)
  geolocation = gis_models.PointField()
  altitude = models.IntegerField(default = 0)
  notes = models.TextField(blank = True, default = "")
  url = models.URLField(verify_exists = False, blank = True, default = "", verbose_name = _("URL"))
  
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
    try:
      self.fields['geolocation'].widget.default_location = [
        item.project.geo_lat,
        item.project.geo_long,
        item.project.geo_zoom
      ]
    except (nodes_models.Project.DoesNotExist, AttributeError):
      pass

registration.point("node.config").register_choice("core.general#type", "wireless", _("Wireless"))
registration.point("node.config").register_choice("core.general#type", "server", _("Server"))
registration.point("node.config").register_choice("core.general#type", "mobile", _("Mobile"))
registration.point("node.config").register_choice("core.general#type", "test", _("Test"))
registration.point("node.config").register_choice("core.general#type", "dead", _("Dead"))
registration.point("node.config").register_choice("core.general#type", "unknown", _("Unknown"))
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

class RoleConfig(registration.bases.NodeConfigRegistryItem):
  """
  Describes a single node's role.
  """
  class RegistryMeta:
    form_order = 20
    registry_id = "core.roles"
    registry_section = _("Node Roles")
    registry_name = _("Generic Role")
    multiple = True
    multiple_static = True
    hidden = True

registration.point("node.config").register_item(RoleConfig)

class SystemRoleConfig(RoleConfig):
  """
  Describes the "system" role.
  """
  system = models.BooleanField(default = False)
  
  class RegistryMeta(RoleConfig.RegistryMeta):
    registry_name = _("System Role")

registration.point("node.config").register_item(SystemRoleConfig)

class BorderRouterRoleConfig(RoleConfig):
  """
  Describes the "border router" role.
  """
  border_router = models.BooleanField(default = False)
  
  class RegistryMeta(RoleConfig.RegistryMeta):
    registry_name = _("Border Router Role")

registration.point("node.config").register_item(BorderRouterRoleConfig)

class VpnServerRoleConfig(RoleConfig):
  """
  Describes the "vpn server" role.
  """
  vpn_server = models.BooleanField(default = False)
  
  class RegistryMeta(RoleConfig.RegistryMeta):
    registry_name = _("VPN Server Role")

registration.point("node.config").register_item(VpnServerRoleConfig)

class RedundantNodeRoleConfig(RoleConfig):
  """
  Describes the "redundant node" role.
  """
  redundancy_required = models.BooleanField(default = False)
  
  class RegistryMeta(RoleConfig.RegistryMeta):
    registry_name = _("Redundant Node Role")

registration.point("node.config").register_item(RedundantNodeRoleConfig)

