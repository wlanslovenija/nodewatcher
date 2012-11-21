from django.utils.translation import ugettext as _

from nodewatcher.core.cgm import models as cgm_models
from nodewatcher.registry.cgm import base as cgm_base
from nodewatcher.registry.cgm import resources as cgm_resources
from nodewatcher.registry.cgm import routers as cgm_routers

@cgm_base.register_platform_module("openwrt", 10)
def general(node, cfg):
  """
  General configuration for nodewatcher firmware.
  """
  system = cfg.system.add("system")
  system.hostname = node.config.core.general().name
  system.uuid = node.uuid
  # TODO timezone should probably not be hardcoded
  system.timezone = "CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00"

  # Setup base packages to be installed
  cfg.packages.update(["nodewatcher-core", "nodewatcher-watchdog"])

def configure_network(cfg, network, section):
  """
  A helper function to configure an interface's network.

  :param cfg: Platform configuration
  :param network: Network configuration
  :param section: UCI interface or alias section
  """
  if isinstance(network, cgm_models.StaticNetworkConfig):
    section.proto = "static"
    if network.family == "ipv4":
      section.ipaddr = network.address.ip
      section.netmask = network.address.netmask
      section.gateway = network.gateway.ip
    elif network.family == "ipv6":
      section.ip6addr = network.address
      section.ip6gw = network.gateway.ip
    else:
      raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
  elif isinstance(network, cgm_models.AllocatedNetworkConfig):
    section.proto = "static"

    # When network is marked to be announced, also specify it here
    if network.routing_announce:
      section._announce = [network.routing_announce]

    if network.family in ("ipv4", "ipv6"):
      # Make our subnet available to other modules as a resource
      res = cgm_resources.IpResource(network.family, network.allocation.ip_subnet, network)
      cfg.resources.add(res)
      address = res.allocate()

      if network.family == "ipv4":
        section.ipaddr = address.ip
        section.netmask = address.netmask
      elif network.family == "ipv6":
        section.ip6addr = address
    else:
      raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
  elif isinstance(network, cgm_models.DHCPNetworkConfig):
    section.proto = "dhcp"
  else:
    section.proto = "none"

def configure_interface(cfg, interface, section, iface_name):
  """
  A helper function to configure an interface.

  :param cfg: Platform configuration
  :param interface: Interface configuration
  :param section: UCI interface section
  :param iface_name: Name of the UCI interface
  """
  section._routable = interface.routing_protocol

  networks = [x.cast() for x in interface.networks.all()]
  if networks:
    network = networks[0]
    configure_network(cfg, network, section)

    # Additional network configurations are aliases
    for network in networks[1:]:
      alias = cfg.network.add("alias")
      alias.interface = iface_name
      configure_network(cfg, network, alias)
  else:
    section.proto = "none"

@cgm_base.register_platform_module("openwrt", 10)
def network(node, cfg):
  """
  Basic network configuration.
  """
  lo = cfg.network.add(interface = "loopback")
  lo.ifname = "lo"
  lo.proto = "static"
  lo.ipaddr = "127.0.0.1"
  lo.netmask = "255.0.0.0"

  # Obtain the router descriptor for this device
  router = node.config.core.general().get_device()

  # Configure all interfaces
  for interface in node.config.core.interfaces():
    if not interface.enabled:
      continue

    if isinstance(interface, cgm_models.EthernetInterfaceConfig):
      iface = cfg.network.add(interface = interface.eth_port)
      iface.ifname = router.remap_port("openwrt", interface.eth_port)
      if iface.ifname is None:
        raise cgm_base.ValidationError(_("No port remapping for port '%s' of router '%s' is available!") % \
          (interface.eth_port, router.name))

      if interface.uplink:
        iface._uplink = True

      configure_interface(cfg, interface, iface, interface.eth_port)
    elif isinstance(interface, cgm_models.WifiRadioDeviceConfig):
      # Configure virtual interfaces on top of the same radio device
      interfaces = list(interface.interfaces.all())
      if len(interfaces) > 1 and cgm_routers.Features.MultipleSSID not in router.features:
        raise cgm_base.ValidationError(_("Router '%s' does not support multiple SSIDs!") % router.name)

      wifi_radio = router.remap_port("openwrt", interface.wifi_radio)
      radio = cfg.wireless.add(**{ "wifi-device" : wifi_radio })

      dsc_radio = router.get_radio(interface.wifi_radio)
      dsc_protocol = dsc_radio.get_protocol(interface.protocol)
      dsc_channel = dsc_protocol.get_channel(interface.channel)
      # TODO protocol details
      radio.phy = "phy%d" % dsc_radio.index
      radio.channel = dsc_channel.number

      for index, vif in enumerate(interfaces):
        wif = cfg.wireless.add("wifi-iface")
        wif.device = wifi_radio
        wif.encryption = "none"
        wif.ssid = vif.essid

        if vif.mode == "ap":
          wif.mode = "ap"
        elif vif.mode == "mesh":
          wif.mode = "adhoc"
          wif.bssid = vif.bssid
        else:
          raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless interface mode '%s'!") % vif.mode)

        # Configure network interface for each vif, first being the primary network
        vif_name = "%sv%d" % (wifi_radio, index)
        iface = cfg.network.add(interface = vif_name)
        wif.network = vif_name

        configure_interface(cfg, vif, iface, vif_name)
