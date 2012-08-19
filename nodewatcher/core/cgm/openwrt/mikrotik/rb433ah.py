from nodewatcher.registry.cgm import base as cgm_base
from nodewatcher.registry.cgm import routers as cgm_routers
from nodewatcher.registry.cgm import protocols as cgm_protocols

class MikrotikRB433AH(cgm_routers.RouterBase):
  """
  Mikrotik RB433AH device descriptor.
  """
  identifier = "rb433ah"
  name = "RB433AH"
  manufacturer = "MikroTik"
  url = "http://routerboard.com/RB433AH"
  architecture = "ar71xx"
  radios = [ 
    # FIXME this information is not correct, there are no integrated radios
    cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG], [
      cgm_routers.AntennaConnector("a1", "Antenna0")
    ])
  ]
  ports = [
    # FIXME this information is possibly not correct
    cgm_routers.EthernetPort("wan0", "Wan0"),
    cgm_routers.EthernetPort("lan0", "Lan0")
  ]
  antennas = [
  ]
  port_map = {
    "openwrt": {
      "wifi0" : "wlan0",
      "wan0"  : "eth1",
      "lan0"  : "eth0",
      }
  }
  
  @cgm_routers.register_module()
  def network(node, cfg):
    """
    Network configuration CGM for Mikrotik RB433AH.
    """
    pass

# Register the Mikrotik RB433AH router
cgm_base.register_router("openwrt", MikrotikRB433AH)

