from web.registry.cgm import base as cgm_base
from web.registry.cgm import routers as cgm_routers
from web.registry.cgm import protocols as cgm_protocols

from web.core.cgm.openwrt.linksys import wrt54gl

class LinksysWRT54GS(wrt54gl.LinksysWRT54GL):
  """
  Linksys WRT54GS device descriptor.
  """
  identifier = "wrt54gs"
  name = "WRT54GS"

# Register the Linksys WRT54GS router
cgm_base.register_router("openwrt", LinksysWRT54GS)

