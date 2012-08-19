from django.utils.translation import ugettext as _

from nodewatcher.registry import registration
from nodewatcher.registry.cgm import base as cgm_base

# Register tunneldigger VPN protocol
registration.point("node.config").register_choice("core.servers.vpn#protocol", "tunneldigger", _("Tunneldigger"))

@cgm_base.register_platform_module("openwrt", 100)
def tunneldigger(node, cfg):
  """
  Configures the tunneldigger VPN solution.
  """
  # Deactivate tunneldigger when no uplink interface has been configured
  uplink_interface = None
  for name, section in cfg.network:
    if section.get_type() == "interface" and section._uplink:
      uplink_interface = name
      break
  else:
    return

  # Create tunneldigger configuration
  brokers = {}
  for server in node.config.core.servers.vpn(queryset = True).filter(protocol = "tunneldigger"):
    brokers.setdefault(server.hostname, []).append(server.port)

  for idx, (address, ports) in enumerate(brokers.items()):
    # Create tunneldigger configurations
    broker = cfg.tunneldigger.add("broker")
    broker.address = address
    broker.port = ports
    broker.uuid = node.uuid
    broker.interface = "digger%d" % idx

    # Create routing policy entries to ensure tunneldigger connections are not
    # routed via the mesh
    policy = cfg.routing.add("policy")
    policy.dest_ip = address
    policy.table = "main"
    policy.priority = 500

    # Create interface configurations; note that addressing configuration is routing
    # daemon dependent and as such should not be filled in here
    iface = cfg.network.add(interface = broker.interface)
    iface.ifname = broker.interface
    iface.proto = "none"
    iface._routable = True

  # Ensure that WAN traffic is routed via the main table
  policy = cfg.routing.add("policy")
  policy.device = uplink_interface
  policy.table = "main"
  policy.priority = 500

# TODO also register the 'tunneldigger' and 'policy-routing' base packages for openwrt platform
