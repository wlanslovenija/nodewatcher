from nodewatcher.core.generator.cgm import base as cgm_base

from . import wrt54gl


class LinksysWRT54GS(wrt54gl.LinksysWRT54GL):
    """
    Linksys WRT54GS device descriptor.
    """

    identifier = 'wrt54gs'
    name = "WRT54GS"

# Register the Linksys WRT54GS router
cgm_base.register_device('openwrt', LinksysWRT54GS)
