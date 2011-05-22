from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.core import allocation
from web.core import models as core_models
from web.nodes import models as nodes_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration

class CgmGeneralConfig(core_models.GeneralConfig):
  """
  Extended general configuration that contains CGM-related options.
  """
  password = models.CharField(max_length = 30)
  platform = registry_fields.SelectorKeyField("node.config", "core.general#platform")
  router = registry_fields.SelectorKeyField("node.config", "core.general#router")
  version = models.CharField(max_length = 20) # TODO fkey to versions (production, experimental, ...)
  
  class RegistryMeta(core_models.GeneralConfig.RegistryMeta):
    registry_name = _("CGM Configuration")

class CgmGeneralConfigForm(forms.ModelForm):
  class Meta:
    model = CgmGeneralConfig

registration.point("node.config").register_item(CgmGeneralConfig)
registration.register_form_for_item(CgmGeneralConfig, CgmGeneralConfigForm)

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

class AllocatedNetworkConfig(CgmNetworkConfig, allocation.AddressAllocator):
  """
  IP configuration that gets allocated from a pool.
  """
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("Allocated Network")

class AllocatedNetworkConfigForm(forms.ModelForm, allocation.AddressAllocatorFormMixin):
  """
  General configuration form.
  """
  class Meta:
    model = AllocatedNetworkConfig

registration.point("node.config").register_choice("core.interfaces.network#usage", "auto", _("Routing and Clients"))
registration.point("node.config").register_choice("core.interfaces.network#usage", "routing", _("Routing Loopback"))
registration.point("node.config").register_choice("core.interfaces.network#usage", "clients", _("Clients"))
registration.point("node.config").register_subitem(EthernetInterfaceConfig, AllocatedNetworkConfig)
registration.point("node.config").unregister_item(core_models.BasicAddressingConfig)
registration.register_form_for_item(AllocatedNetworkConfig, AllocatedNetworkConfigForm)

class PPPoENetworkConfig(CgmNetworkConfig):
  """
  Configuration for a WAN PPPoE uplink.
  """
  username = models.CharField(max_length = 50)
  password = models.CharField(max_length = 50)
  
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("PPPoE")

registration.point("node.config").register_subitem(EthernetInterfaceConfig, PPPoENetworkConfig)

class WifiNetworkConfig(CgmNetworkConfig, allocation.AddressAllocator):
  """
  Configuration for a WiFi network.
  """
  role = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#role")
  essid = models.CharField(max_length = 50)
  bssid = registry_fields.MACAddressField()
  
  class RegistryMeta(CgmNetworkConfig.RegistryMeta):
    registry_name = _("WiFi Network")

class WifiNetworkConfigForm(forms.ModelForm, allocation.AddressAllocatorFormMixin):
  """
  General configuration form.
  """
  class Meta:
    model = WifiNetworkConfig

registration.point("node.config").register_choice("core.interfaces.network#role", "mesh", _("Mesh"))
registration.point("node.config").register_choice("core.interfaces.network#role", "endusers", _("Endusers"))
registration.point("node.config").register_choice("core.interfaces.network#role", "backbone-ap", _("Backbone-AP"))
registration.point("node.config").register_choice("core.interfaces.network#role", "backbone-sta", _("Backbone-STA"))
registration.point("node.config").register_subitem(WifiInterfaceConfig, WifiNetworkConfig)
registration.register_form_for_item(WifiNetworkConfig, WifiNetworkConfigForm)

class VpnServerConfig(registration.bases.NodeConfigRegistryItem):
  """
  Provides a VPN server specification that the nodes can use.
  """
  protocol = registry_fields.SelectorKeyField("node.config", "core.vpn.server#protocol")
  hostname = models.CharField(max_length = 100)
  port = models.IntegerField()
  
  class RegistryMeta:
    form_order = 2
    registry_id = "core.vpn.server"
    registry_section = _("VPN Servers")
    registry_name = _("VPN Server")
    multiple = True

class VpnServerConfigForm(forms.ModelForm):
  """
  VPN server configuration form.
  """
  port = forms.IntegerField(min_value = 1, max_value = 49151)
  
  class Meta:
    model = VpnServerConfig

registration.point("node.config").register_item(VpnServerConfig)
registration.register_form_for_item(VpnServerConfig, VpnServerConfigForm)

