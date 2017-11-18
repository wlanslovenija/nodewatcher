from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRBwAP2nD(cgm_devices.DeviceBase):
    """
    Mikrotik RB wAP 2nD (wAP) device descriptor.
    """

    identifier = 'mt-rbwap-2nd'
    name = "wAP (RBwAP2nD)"
    manufacturer = "MikroTik"
    url = 'https://mikrotik.com/product/RBwAP2nD'
    architecture = 'ar71xx_mikrotik'
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
            'name': 'rb-nor-flash-16M',
            'files': [
                '*-ar71xx-mikrotik-rb-nor-flash-16M-squashfs-sysupgrade.bin',
            ]
        }
    }

# Register the Mikrotik wAP devices.
cgm_base.register_device('lede', MikrotikRBwAP2nD)
