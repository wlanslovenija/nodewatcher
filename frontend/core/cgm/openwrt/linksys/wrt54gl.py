from frontend.registry.cgm import base as cgm_base
from frontend.registry.cgm import routers as cgm_routers
from frontend.registry.cgm import protocols as cgm_protocols

class LinksysWRT54GL(cgm_routers.RouterBase):
  """
  Linksys WRT54GL device descriptor.
  """
  identifier = "wrt54gl"
  name = "WRT54GL"
  manufacturer = "Linksys"
  url = "http://www.linksysbycisco.com/"
  architecture = "brcm47xx"
  radios = [
    cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG], [
      cgm_routers.AntennaConnector("a1", "Antenna0"),
      cgm_routers.AntennaConnector("a2", "Antenna1")
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
    Network configuration CGM for Linksys WRT54GL.
    """
    pass

# Register the Linksys WRT54GL router
cgm_base.register_router("openwrt", LinksysWRT54GL)

