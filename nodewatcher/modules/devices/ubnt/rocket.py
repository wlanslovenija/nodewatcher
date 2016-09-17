from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTRocketM2(cgm_devices.DeviceBase):
    """
    UBNT Rocket M2 device descriptor.
    """

    identifier = 'ub-rocket-m2'
    name = "Rocket M2"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.TX_STBC1,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
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
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'UBNT',
            'files': [
                'openwrt-ar71xx-generic-ubnt-rocket-m-squashfs-factory.bin',
                'openwrt-ar71xx-generic-ubnt-rocket-m-squashfs-sysupgrade.bin',
            ]
        }
    }


class UBNTRocketM5(UBNTRocketM2):
    """
    UBNT Rocket M5 device descriptor.
    """

    identifier = 'ub-rocket-m5'
    name = "Rocket M5"
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
                cgm_protocols.IEEE80211AN.TX_STBC1,
                cgm_protocols.IEEE80211AN.RX_STBC1,
                cgm_protocols.IEEE80211AN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]


class UBNTRocketM5XW(UBNTRocketM5):
    """
    UBNT Rocket M5 XW device descriptor.
    """

    identifier = 'ub-rocket-m5-xw'
    name = "Rocket M5 XW"
    profiles = {
        'openwrt': {
            'name': 'UBNT',
            'files': [
                'openwrt-ar71xx-generic-ubnt-rocket-m-xw-squashfs-factory.bin',
                'openwrt-ar71xx-generic-ubnt-rocket-m-xw-squashfs-sysupgrade.bin',
            ]
        }
    }

# Register the UBNT Rocket devices.
cgm_base.register_device('openwrt', UBNTRocketM2)
cgm_base.register_device('openwrt', UBNTRocketM5)
cgm_base.register_device('openwrt', UBNTRocketM5XW)
