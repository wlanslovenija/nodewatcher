from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTAPACLite(cgm_devices.DeviceBase):
    """
    Ubiquiti AP AC Lite device descriptor.
    """

    identifier = 'ub-uap-ac-lite'
    name = "Unifi AP AC Lite"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio (5 GHz)"), [
            cgm_protocols.IEEE80211AC(
                cgm_protocols.IEEE80211AC.SHORT_GI_20,
                cgm_protocols.IEEE80211AC.SHORT_GI_40,
                cgm_protocols.IEEE80211AC.RX_STBC1,
                cgm_protocols.IEEE80211AC.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ]),
        cgm_devices.IntegratedRadio('wifi1', _("Integrated wireless radio (2.4 GHz)"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a2', "Antenna2")
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
            polarization='dual',
            angle_horizontal=360,
            angle_vertical=120,
            gain=3,
        ),
        cgm_devices.InternalAntenna(
            identifier='a2',
            polarization='dual',
            angle_horizontal=360,
            angle_vertical=120,
            gain=3,
        )
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'wifi1': 'radio1',
            'lan0': 'eth0',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
            'wifi1': 'mac80211',
        }
    }
    profiles = {
        'lede': {
            'name': 'ubnt-unifiac-lite',
            'files': [
                '*-ar71xx-generic-ubnt-unifiac-lite-squashfs-sysupgrade.bin',
            ]
        }
    }


class UBNTUap(cgm_devices.DeviceBase):
    """
    UBNT Unifi UAP device descriptor.
    """

    identifier = 'ub-uap'
    name = "Unifi UAP"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi1', _("Integrated wireless radio (2.4 GHz)"), [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('lan0', "Lan0")
    ]
    antennas = [
        cgm_devices.InternalAntenna(
            identifier='a1',
            polarization='dual',
            angle_horizontal=360,
            angle_vertical=120,
            gain=3,
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
            'name': 'ubnt-unifi',
            'files': [
                '*-ar71xx-generic-ubnt-unifi-squashfs-factory.bin',
                '*-ar71xx-generic-ubnt-unifi-squashfs-sysupgrade.bin',
            ]
        }
    }


class UBNTUapLR(UBNTUap):
    """
    UBNT Unifi UAP-LR device descriptor.
    """

    identifier = 'ub-uap-lr'
    name = "Unifi UAP-LR"


# Register Unifi AP devices.
cgm_base.register_device('lede', UBNTAPACLite)
cgm_base.register_device('lede', UBNTUap)
cgm_base.register_device('lede', UBNTUapLR)
