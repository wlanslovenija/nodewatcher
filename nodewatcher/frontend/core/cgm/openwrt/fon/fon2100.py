from frontend.registry.cgm import base as cgm_base
from frontend.registry.cgm import routers as cgm_routers
from frontend.registry.cgm import protocols as cgm_protocols

class Fonera(cgm_routers.RouterBase):
  """
  Fonera FON-2100 device descriptor.
  """
  identifier = "fon-2100"
  name = "Fonera"
  manufacturer = "Fon Wireless Ltd."
  url = "http://www.fon.com"
  architecture = "atheros"
  radios = [
    cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG], [
      cgm_routers.AntennaConnector("a1", "Antenna0")
    ])
  ]
  ports = [
    cgm_routers.EthernetPort("wan0", "Ethernet0")
  ]
  antennas = [
    cgm_routers.InternalAntenna(
      identifier = "a1",
      polarization = "horizontal",
      angle_horizontal = 360,
      angle_vertical = 75,
      gain = 2
    )
  ]
  
  @cgm_routers.register_module()
  def network(node, cfg):
    """
    Network configuration CGM for FON-2100.
    """
    pass

# Register the FON-2100 router
cgm_base.register_router("openwrt", Fonera)

