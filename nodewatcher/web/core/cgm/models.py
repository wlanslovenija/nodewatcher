from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from registry import fields as registry_fields
from registry import forms as registry_forms
from registry import registration

class CgmPackageConfig(registration.bases.NodeConfigRegistryItem):
  """
  Common configuration for CGM packages.
  """
  enabled = models.BooleanField(default = True)
  
  class RegistryMeta:
    form_order = 100
    registry_id = "core.packages"
    registry_section = _("Extra Packages")
    registry_name = _("Package Configuration")
    multiple = True
    hidden = True

registration.point("node.config").register_item(CgmPackageConfig)

class CgmInterfaceConfig(registration.bases.NodeConfigRegistryItem):
  """
  Interface configuration.
  """
  enabled = models.BooleanField(default = True)
  
  class RegistryMeta:
    form_order = 50
    registry_id = "core.interfaces"
    registry_section = _("Network Interface Configuration")
    registry_name = _("Generic Interface")
    multiple = True
    hidden = True

registration.point("node.config").register_item(CgmInterfaceConfig)

class EthernetInterfaceConfig(CgmInterfaceConfig):
  """
  An ethernet interface.
  """
  eth_port = registry_fields.SelectorKeyField("node.config", "core.interfaces#eth_port")
  
  class RegistryMeta(CgmInterfaceConfig.RegistryMeta):
    registry_name = _("Ethernet Interface")

registration.point("node.config").register_item(EthernetInterfaceConfig)

class WifiInterfaceConfig(CgmInterfaceConfig):
  """
  A wireless interface.
  """
  wifi_radio = registry_fields.SelectorKeyField("node.config", "core.interfaces#wifi_radio")
  protocol = models.CharField(max_length = 50) # TODO should be a registered choice (router-dep)
  channel = models.IntegerField(default = 8) # TODO should be a registered choice (proto-dep)
  bitrate = models.IntegerField(default = 11) # TODO should be a registered choice (proto-dep)
  
  class RegistryMeta(CgmInterfaceConfig.RegistryMeta):
    registry_name = _("Wireless Radio")

registration.point("node.config").register_item(WifiInterfaceConfig)

class CgmNetworkConfig(registration.bases.NodeConfigRegistryItem):
  """
  Network configuration of an interface.
  """
  interface = registry_fields.IntraRegistryForeignKey(CgmInterfaceConfig, editable = False, null = False, related_name = 'networks')
  enabled = models.BooleanField(default = True)
  description = models.CharField(max_length = 100)
  
  class RegistryMeta:
    form_order = 51
    registry_id = "core.interfaces.network"
    registry_section = _("Network Configuration")
    registry_name = _("Generic Network Config")
    multiple = True
    hidden = True

registration.point("node.config").register_subitem(CgmInterfaceConfig, CgmNetworkConfig)

class StaticNetworkConfig(CgmNetworkConfig):
  """
  Static IP configuration.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#family")
  
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("Static Network")

registration.point("node.config").register_choice("core.interfaces.network#family", "ipv4", _("IPv4"))
registration.point("node.config").register_choice("core.interfaces.network#family", "ipv6", _("IPv6"))
registration.point("node.config").register_subitem(EthernetInterfaceConfig, StaticNetworkConfig)

class PPPoENetworkConfig(CgmNetworkConfig):
  """
  Configuration for a WAN PPPoE uplink.
  """
  username = models.CharField(max_length = 50)
  password = models.CharField(max_length = 50)
  
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("PPPoE")

registration.point("node.config").register_subitem(EthernetInterfaceConfig, PPPoENetworkConfig)

class WifiNetworkConfig(CgmNetworkConfig):
  """
  Configuration for a WiFi network.
  """
  role = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#role")
  essid = models.CharField(max_length = 50)
  bssid = models.CharField(max_length = 50) # TODO should be a validated mac address
  
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("WiFi Network")

registration.point("node.config").register_choice("core.interfaces.network#role", "mesh", _("Mesh"))
registration.point("node.config").register_choice("core.interfaces.network#role", "endusers", _("Endusers"))
registration.point("node.config").register_choice("core.interfaces.network#role", "backbone-ap", _("Backbone-AP"))
registration.point("node.config").register_choice("core.interfaces.network#role", "backbone-sta", _("Backbone-STA"))
registration.point("node.config").register_subitem(WifiInterfaceConfig, WifiNetworkConfig)

