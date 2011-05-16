from registry.cgm import base as cgm_base
from registry.cgm import routers as cgm_routers

class Fonera(cgm_routers.RouterBase):
  """
  Fonera FON-2100 device descriptor.
  """
  identifier = "fon-2100"
  name = "Fonera"
  architecture = "atheros"
  radios = [
    cgm_routers.IntegratedRadio("ath0", "Wifi0")
  ]
  ports = [
    cgm_routers.EthernetPort("eth0", "Ethernet0")
  ]
  
  @cgm_routers.register_module()
  def network(node, cfg):
    """
    Network configuration CGM for FON-2100.
    """
    pass

# Register the FON-2100 router
cgm_base.register_router("openwrt", Fonera)

