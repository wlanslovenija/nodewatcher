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
  node.
  """
  name = models.CharField(max_length = 30)
  type = registry_fields.SelectorKeyField("node.config", "core.general#type")
  
  class RegistryMeta:
    form_order = 1
    registry_id = "core.general"
    registry_section = _("General Configuration")
    registry_name = _("Basic Configuration")
    lookup_proxies = []

# TODO validate node name via regexp: NODE_NAME_RE = re.compile(r'^[a-z](?:-?[a-z0-9]+)*$')

registration.point("node.config").register_choice("core.general#type", "wireless", _("Wireless"))
registration.point("node.config").register_choice("core.general#type", "server", _("Server"))
registration.point("node.config").register_choice("core.general#type", "mobile", _("Mobile"))
registration.point("node.config").register_choice("core.general#type", "test", _("Test"))
registration.point("node.config").register_choice("core.general#type", "dead", _("Dead"))
registration.point("node.config").register_choice("core.general#type", "unknown", _("Unknown"))
registration.point("node.config").register_item(GeneralConfig)

class ProjectConfig(registration.bases.NodeConfigRegistryItem):
  """
  Describes the project a node belongs to.
  """
  project = registry_fields.ModelSelectorKeyField("nodes.Project")
  
  class RegistryMeta:
    form_order = 2
    registry_id = "core.project"
    registry_section = _("Project")
    registry_name = _("Basic Project")

registration.point("node.config").register_item(ProjectConfig)

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
    registry_id = "core.location"
    registry_section = _("Location")
    registry_name = _("Basic Location")

class LocationConfigForm(forms.ModelForm):
  """
  Location configuration form.
  """
  class Meta:
    model = LocationConfig
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
      project = cfg['core.project'][0].project
      
      self.fields['geolocation'].widget.default_location = [
        project.geo_lat,
        project.geo_long,
        project.geo_zoom
      ]
    except (nodes_models.Project.DoesNotExist, AttributeError, KeyError, IndexError):
      pass

registration.point("node.config").register_item(LocationConfig)
registration.register_form_for_item(LocationConfig, LocationConfigForm)

class DescriptionConfig(registration.bases.NodeConfigRegistryItem):
  """
  Textual description of a node.
  """
  notes = models.TextField(blank = True, default = "")
  url = models.URLField(verify_exists = False, blank = True, default = "", verbose_name = _("URL"))
  
  class RegistryMeta:
    form_order = 4
    registry_id = "core.description"
    registry_section = _("Description")
    registry_name = _("Basic Description")

registration.point("node.config").register_item(DescriptionConfig)

class BasicAddressingConfig(registration.bases.NodeConfigRegistryItem, allocation.IpAddressAllocator):
  """
  Enables allocation of subnets for the node without the need to define any interfaces.
  """
  class RegistryMeta:
    form_order = 51
    registry_id = "core.basic-addressing"
    registry_section = _("Subnet Allocation")
    registry_name = _("Subnet")
    multiple = True

class BasicAddressingConfigForm(forms.ModelForm, allocation.IpAddressAllocatorFormMixin):
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

