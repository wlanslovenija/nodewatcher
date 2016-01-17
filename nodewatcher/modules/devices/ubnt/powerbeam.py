from nodewatcher.core.generator.cgm import base as cgm_base

from . import rocket, nano


class UBNTPowerBeamM5300(nano.UBNTLocoM5XW):
    """
    UBNT PowerBeam M5 300 device descriptor.
    """

    identifier = 'ub-powerbeam-m5-300'
    name = "PowerBeam M5 300"


class UBNTPowerBeamM5400(rocket.UBNTRocketM5XW):
    """
    UBNT PowerBeam M5 400 device descriptor.
    """

    identifier = 'ub-powerbeam-m5-400'
    name = "PowerBeam M5 400"


class UBNTPowerBeamM5620(UBNTPowerBeamM5400):
    """
    UBNT PowerBeam M5 620 device descriptor.
    """

    identifier = 'ub-powerbeam-m5-620'
    name = "PowerBeam M5 620"

# Register the UBNT PowerBeam devices.
cgm_base.register_device('openwrt', UBNTPowerBeamM5300)
cgm_base.register_device('openwrt', UBNTPowerBeamM5400)
cgm_base.register_device('openwrt', UBNTPowerBeamM5620)
