from django import forms
from django.core import exceptions
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import ugettext as _

from web.core import allocation
from web.core import models as core_models
from web.core import antennas as core_antennas
from web.nodes import models as nodes_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration, permissions
from web.registry.cgm import base as cgm_base

# Register a new firmware-generating permission
permissions.register(nodes_models.Node, 'can_generate_firmware', "Can generate firmware")

class CgmGeneralConfig(core_models.GeneralConfig):
  """
  Extended general configuration that contains CGM-related options.
  """
  platform = registry_fields.SelectorKeyField("node.config", "core.general#platform", blank = True)
  router = registry_fields.SelectorKeyField("node.config", "core.general#router", blank = True)
  version = models.CharField(max_length = 20, blank = True) # TODO fkey to versions (production, experimental, ...)
  
  class RegistryMeta(core_models.GeneralConfig.RegistryMeta):
    registry_name = _("CGM Configuration")
    hides_parent = True

registration.point("node.config").register_item(CgmGeneralConfig)

class AuthenticationConfig(registration.bases.NodeConfigRegistryItem):
  """
  Configuration for different authentication mechanisms.
  """
  class RegistryMeta:
    form_order = 10
    registry_id = "core.authentication"
    registry_section = _("Authentication")
    registry_name = _("Basic Authentication")
    multiple = True
    hidden = True

registration.point("node.config").register_item(AuthenticationConfig)

class PasswordAuthenticationConfig(AuthenticationConfig):
  """
  Password authentication mechanism configuration.
  """
  password = models.CharField(max_length = 30)
  
  class RegistryMeta(AuthenticationConfig.RegistryMeta):
    registry_name = _("Password")

registration.point("node.config").register_item(PasswordAuthenticationConfig)

class PublicKeyAuthenticationConfig(AuthenticationConfig):
  """
  Public key authentication mechanism configuration.
  """
  public_key = models.TextField()
  
  class RegistryMeta(AuthenticationConfig.RegistryMeta):
    registry_name = _("Public Key")

registration.point("node.config").register_item(PublicKeyAuthenticationConfig)

class PackageConfig(registration.bases.NodeConfigRegistryItem):
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

registration.point("node.config").register_item(PackageConfig)

class InterfaceConfig(registration.bases.NodeConfigRegistryItem):
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

registration.point("node.config").register_item(InterfaceConfig)

class EthernetInterfaceConfig(InterfaceConfig):
  """
  An ethernet interface.
  """
  eth_port = registry_fields.SelectorKeyField("node.config", "core.interfaces#eth_port")
  
  class RegistryMeta(InterfaceConfig.RegistryMeta):
    registry_name = _("Ethernet Interface")

registration.point("node.config").register_item(EthernetInterfaceConfig)

class WifiInterfaceConfig(InterfaceConfig):
  """
  A wireless interface.
  """
  wifi_radio = registry_fields.SelectorKeyField("node.config", "core.interfaces#wifi_radio")
  protocol = models.CharField(max_length = 50)
  channel = models.CharField(max_length = 50)
  bitrate = models.IntegerField(default = 11)
  antenna_connector = models.CharField(max_length = 50, null = True)
  antenna = registry_fields.ModelSelectorKeyField(core_antennas.Antenna, null = True)
  
  class RegistryMeta(InterfaceConfig.RegistryMeta):
    registry_name = _("Wireless Radio")

class WifiInterfaceConfigForm(forms.ModelForm, core_antennas.AntennaReferencerFormMixin):
  """
  A wireless interface configuration form.
  """
  class Meta:
    model = WifiInterfaceConfig
  
  def regulatory_filter(self):
    """
    Subclasses may override this method to filter the channels accoording to a
    filter for a regulatory domain. It should return a list of frequencies that
    are allowed.
    """
    return None
  
  def modify_to_context(self, item, cfg, request):
    """
    Handles dynamic protocol/channel selection.
    """
    super(WifiInterfaceConfigForm, self).modify_to_context(item, cfg, request)
    radio = None
    try:
      radio = cgm_base.get_platform(cfg['core.general'][0].platform) \
                      .get_router(cfg['core.general'][0].router) \
                      .get_radio(item.wifi_radio)
      
      # Protocols
      self.fields['protocol'] = registry_fields.SelectorFormField(
        label = _("Protocol"),
        choices = BLANK_CHOICE_DASH + list(radio.get_protocol_choices()),
        coerce = str,
        empty_value = None
      )
      
      # Antenna connectors
      self.fields['antenna_connector'] = registry_fields.SelectorFormField(
        label = _("Connector"),
        choices = [("", _("[auto-select]"))] + list(radio.get_connector_choices()),
        coerce = str,
        empty_value = None,
        required = False
      )
    except (KeyError, IndexError, AttributeError):
      # Create empty fields on error
      self.fields['protocol'] = registry_fields.SelectorFormField(label = _("Protocol"), choices = BLANK_CHOICE_DASH)
      self.fields['channel'] = registry_fields.SelectorFormField(label = _("Channel"), choices = BLANK_CHOICE_DASH)
      self.fields['antenna_connector'] = registry_fields.SelectorFormField(label = _("Connector"), choices = BLANK_CHOICE_DASH)
      return
    
    # Channels
    try:
      self.fields['channel'] = registry_fields.SelectorFormField(
        label = _("Channel"),
        choices = BLANK_CHOICE_DASH + list(radio.get_protocol(item.protocol).get_channel_choices(self.regulatory_filter())),
        coerce = str,
        empty_value = None
      )
    except (KeyError, AttributeError):
      # Create empty field on error
      self.fields['channel'] = registry_fields.SelectorFormField(label = _("Channel"), choices = BLANK_CHOICE_DASH)

registration.register_form_for_item(WifiInterfaceConfig, WifiInterfaceConfigForm)
registration.point("node.config").register_item(WifiInterfaceConfig)

class VpnInterfaceConfig(InterfaceConfig):
  """
  VPN interface.
  """
  mac = registry_fields.MACAddressField(auto_add = True)
  
  class RegistryMeta(InterfaceConfig.RegistryMeta):
    registry_name = _("VPN Tunnel")

registration.point("node.config").register_item(VpnInterfaceConfig)

class NetworkConfig(registration.bases.NodeConfigRegistryItem):
  """
  Network configuration of an interface.
  """
  interface = registry_fields.IntraRegistryForeignKey(InterfaceConfig, editable = False, null = False, related_name = 'networks')
  enabled = models.BooleanField(default = True)
  description = models.CharField(max_length = 100)
  
  class RegistryMeta:
    form_order = 51
    registry_id = "core.interfaces.network"
    registry_section = _("Network Configuration")
    registry_name = _("Generic Network Config")
    multiple = True
    hidden = True

registration.point("node.config").register_subitem(InterfaceConfig, NetworkConfig)

class StaticNetworkConfig(NetworkConfig):
  """
  Static IP configuration.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#ip_family")
  address = registry_fields.IPAddressField(subnet_required = True)
  gateway = registry_fields.IPAddressField(host_required = True)
  
  class RegistryMeta(NetworkConfig.RegistryMeta):
    registry_name = _("Static Network")
  
  def clean(self):
    """
    Verifies that gateway is in the address subnet.
    """
    if not self.address or not self.gateway:
      return
    
    family = 6 if self.family == "ipv6" else 4
    if not (self.address.version == self.gateway.version == family):
      raise exceptions.ValidationError(_("You must specify IP addresses of the selected address family!"))
    
    if self.gateway not in self.address:
      raise exceptions.ValidationError(_("Specified gateway is not part of the host's subnet!"))
    
    if self.gateway.ip == self.address.ip:
      raise exceptions.ValidationError(_("Host address and gateway address must be different!"))

registration.point("node.config").register_choice("core.interfaces.network#ip_family", "ipv4", _("IPv4"))
registration.point("node.config").register_choice("core.interfaces.network#ip_family", "ipv6", _("IPv6"))
registration.point("node.config").register_subitem(EthernetInterfaceConfig, StaticNetworkConfig)

class DHCPNetworkConfig(NetworkConfig):
  """
  DHCP IP configuration.
  """
  # No additional fields
  
  class RegistryMeta(NetworkConfig.RegistryMeta):
    registry_name = _("DHCP")

registration.point("node.config").register_subitem(EthernetInterfaceConfig, DHCPNetworkConfig)

class AllocatedNetworkConfig(NetworkConfig, allocation.IpAddressAllocator):
  """
  IP configuration that gets allocated from a pool.
  """
  class RegistryMeta(NetworkConfig.RegistryMeta):
    registry_name = _("Allocated Network")

class AllocatedNetworkConfigForm(forms.ModelForm, allocation.IpAddressAllocatorFormMixin):
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

class PPPoENetworkConfig(NetworkConfig):
  """
  Configuration for a WAN PPPoE uplink.
  """
  username = models.CharField(max_length = 50)
  password = models.CharField(max_length = 50)
  
  class RegistryMeta(NetworkConfig.RegistryMeta):
    registry_name = _("PPPoE")

registration.point("node.config").register_subitem(EthernetInterfaceConfig, PPPoENetworkConfig)

class WifiNetworkConfig(NetworkConfig, allocation.IpAddressAllocator):
  """
  Configuration for a WiFi network.
  """
  role = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#role")
  essid = models.CharField(max_length = 50, verbose_name = "ESSID")
  bssid = registry_fields.MACAddressField(verbose_name = "BSSID")
  
  class RegistryMeta(NetworkConfig.RegistryMeta):
    registry_name = _("WiFi Network")

class WifiNetworkConfigForm(forms.ModelForm, allocation.IpAddressAllocatorFormMixin):
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

class InterfaceLimitConfig(registration.bases.NodeConfigRegistryItem):
  """
  Configuration of per-interface traffic limits.
  """
  interface = registry_fields.IntraRegistryForeignKey(InterfaceConfig, editable = False, null = False, related_name = 'limits')
  enabled = models.BooleanField(default = True)
  
  class RegistryMeta:
    form_order = 50
    registry_id = "core.interfaces.limits"
    registry_section = _("Traffic Limits Configuration")
    registry_name = _("Generic Limits")
    multiple = True
    hidden = True

registration.point("node.config").register_subitem(InterfaceConfig, InterfaceLimitConfig)

class ThroughputInterfaceLimitConfig(InterfaceLimitConfig):
  """
  Throughput limit configuration.
  """
  limit_out = registry_fields.SelectorKeyField("node.config", "core.interfaces.limits#speeds",
    verbose_name = _("Limit OUT"), default = "", blank = True)
  limit_in = registry_fields.SelectorKeyField("node.config", "core.interfaces.limits#speeds",
    verbose_name = _("Limit IN"), default = "", blank = True)
  
  class RegistryMeta(InterfaceLimitConfig.RegistryMeta):
    registry_name = _("Throughput Limit")

registration.point("node.config").register_choice("core.interfaces.limits#speeds", "128kbit", _("128 Kbit/s"))
registration.point("node.config").register_choice("core.interfaces.limits#speeds", "256kbit", _("256 Kbit/s"))
registration.point("node.config").register_choice("core.interfaces.limits#speeds", "512kbit", _("512 Kbit/s"))
registration.point("node.config").register_choice("core.interfaces.limits#speeds", "1mbit", _("1 Mbit/s"))
registration.point("node.config").register_choice("core.interfaces.limits#speeds", "2mbit", _("2 Mbit/s"))
registration.point("node.config").register_choice("core.interfaces.limits#speeds", "4mbit", _("4 Mbit/s"))
registration.point("node.config").register_subitem(VpnInterfaceConfig, ThroughputInterfaceLimitConfig)

class VpnServerConfig(registration.bases.NodeConfigRegistryItem):
  """
  Provides a VPN server specification that the nodes can use.
  """
  protocol = registry_fields.SelectorKeyField("node.config", "core.vpn.server#protocol")
  hostname = models.CharField(max_length = 100)
  port = models.IntegerField()
  
  class RegistryMeta:
    form_order = 20
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

