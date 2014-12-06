from nodewatcher.core.generator.cgm import base as cgm_base

from . import wr841nd


class TPLinkWR941NDv2(wr841nd.TPLinkWR841NDv1):
    """
    TP-Link WR941NDv2 device descriptor.
    """

    identifier = 'tp-wr941ndv2'
    name = "WR941ND (v2)"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    profiles = {
        'openwrt': {
            'name': 'TLWR941',
            'files': [
                'openwrt-ar71xx-generic-tl-wr941nd-v2-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR941NDv3(TPLinkWR941NDv2):
    """
    TP-Link WR941NDv3 device descriptor.
    """

    identifier = 'tp-wr941ndv3'
    name = "WR941ND (v3)"
    profiles = {
        'openwrt': {
            'name': 'TLWR941',
            'files': [
                'openwrt-ar71xx-generic-tl-wr941nd-v3-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR941NDv4(TPLinkWR941NDv2):
    """
    TP-Link WR941NDv4 device descriptor.
    """

    identifier = 'tp-wr941ndv4'
    name = "WR941ND (v4)"
    profiles = {
        'openwrt': {
            'name': 'TLWR941',
            'files': [
                'openwrt-ar71xx-generic-tl-wr941nd-v4-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link WR941ND device
cgm_base.register_device('openwrt', TPLinkWR941NDv2)
cgm_base.register_device('openwrt', TPLinkWR941NDv3)
cgm_base.register_device('openwrt', TPLinkWR941NDv4)
