from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTPicoM2(cgm_devices.DeviceBase):
    """
    UBNT Picostation M2 device descriptor.
    """

    identifier = 'ub-pico-m2'
    name = "Picostation M2"
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
                '*-ar71xx-generic-ubnt-bullet-m-squashfs-factory.bin',
                '*-ar71xx-generic-ubnt-bullet-m-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'ubnt-bullet-m',
            'files': [
                '*-ar71xx-generic-ubnt-bullet-m-squashfs-factory.bin',
                '*-ar71xx-generic-ubnt-bullet-m-squashfs-sysupgrade.bin',
            ]
        }
    }

# Register the UBNT Picostation device.
cgm_base.register_device('openwrt', UBNTPicoM2)
