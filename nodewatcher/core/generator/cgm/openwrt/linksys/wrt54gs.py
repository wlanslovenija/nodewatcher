from nodewatcher.core.registry.cgm import base as cgm_base
from nodewatcher.core.registry.cgm import routers as cgm_routers
from nodewatcher.core.registry.cgm import protocols as cgm_protocols

from nodewatcher.core.generator.cgm.openwrt.linksys import wrt54gl

class LinksysWRT54GS(wrt54gl.LinksysWRT54GL):
    """
    Linksys WRT54GS device descriptor.
    """
    identifier = "wrt54gs"
    name = "WRT54GS"

# Register the Linksys WRT54GS router
cgm_base.register_router("openwrt", LinksysWRT54GS)
