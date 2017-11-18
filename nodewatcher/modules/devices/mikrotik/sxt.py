from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRBSXT5nDr2(cgm_devices.DeviceBase):
    """
    Mikrotik RB SXT5 nDr2 (SXT Lite 5) device descriptor.
    """

    identifier = 'mt-rbsxt5-ndr2'
    name = "RBSXT5nDr2 (SXT Lite 5)"
    manufacturer = "MikroTik"
    url = 'https://mikrotik.com/product/RBSXT5nDr2'
    architecture = 'ar71xx_mikrotik'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_20,
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
                cgm_protocols.IEEE80211AN.RX_STBC1,
                cgm_protocols.IEEE80211AN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('lan0', "Lan0")
    ]
    antennas = [
        # TODO: This information is probably not correct
        cgm_devices.InternalAntenna(
            identifier='a1',
            polarization='horizontal',
            angle_horizontal=360,
            angle_vertical=75,
            gain=2,
        )
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'lan0': 'eth0',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
        }
    }
    profiles = {
        'lede': {
            'name': 'nand-large',
            'files': [
                '*-ar71xx-mikrotik-nand-large-squashfs-sysupgrade.bin'
            ],
        }
    }


class MikrotikRBSXT2nDr2(MikrotikRBSXT5nDr2):
    """
    Mikrotik RB SXT2 nDr2 (SXT Lite 2) device descriptor.
    """

    identifier = 'mt-rbsxt2-ndr2'
    name = "RBSXT2nDr2 (SXT Lite 2)"
    url = 'https://mikrotik.com/product/RBSXT2nDr2'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]

# Register the Mikrotik SXT devices.
cgm_base.register_device('lede', MikrotikRBSXT5nDr2)
cgm_base.register_device('lede', MikrotikRBSXT2nDr2)
