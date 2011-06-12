from web.registry.cgm import base as cgm_base
from web.registry.cgm import routers as cgm_routers
from web.registry.cgm import protocols as cgm_protocols

class BuffaloWHR_HP_G54(cgm_routers.RouterBase):
  """
  Buffalo WHR-HP-G54 device descriptor.
  """
  identifier = "whr-hp-g54"
  name = "WHR-HP-G54"
  manufacturer = "Buffalo Technology Ltd."
  url = "http://www.buffalo-technology.com/"
  architecture = "brcm47xx"
  radios = [
    cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG], [
      cgm_routers.AntennaConnector("a1", "Antenna0")
    ])
  ]
  ports = [
    cgm_routers.EthernetPort("wan0", "Wan0"),
    cgm_routers.EthernetPort("lan0", "Lan0")
  ]
  antennas = [
    # TODO this information is probably not correct
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
    Network configuration CGM for Buffalo WHR-HP-G54.
    """
    pass

# Register the Buffalo WHR-HP-G54 router
cgm_base.register_router("openwrt", BuffaloWHR_HP_G54)

