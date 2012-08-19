from django.utils.translation import ugettext as _

from nodewatcher.core.cgm import models as cgm_models
from nodewatcher.registry.cgm import base as cgm_base
from nodewatcher.registry.cgm import resources as cgm_resources

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

def configure_network(cfg, network, section, routable = False):
  """
  A helper function to configure an interface's network.

  :param cfg: Platform configuration
  :param network: Network configuration
  :param section: UCI interface or alias section
  :param routable: True if this interface has a routing protocol
    configured
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
    print network
    section.proto = "none"

  # Mark the section as being the uplink for this node
  if network.uplink:
    section._uplink = True

  # Mark the section as being routable when configured
  if routable:
    section._routable = True

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

      # Configure network settings
      networks = [x.cast() for x in interface.networks.all()]
      if networks:
        network = networks[0]
        configure_network(cfg, network, iface, routable = (iface.routing_protocol != "none"))

        # Additional network configurations are aliases
        for network in networks[1:]:
          alias = cfg.network.add("alias")
          alias.interface = interface.eth_port
          configure_network(cfg, network, alias)
      else:
        iface.proto = "none"
    #elif isinstance(interface, cgm_models.W)
