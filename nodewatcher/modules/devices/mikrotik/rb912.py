from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRB912UAG_2HPnD(cgm_devices.DeviceBase):
    """
    Mikrotik RB 912UAG-2HPnD device descriptor.
    """

    identifier = 'mt-rb912uag-2hpnd'
    name = "RB912UAG-2HPnD"
    manufacturer = "MikroTik"
    url = 'https://mikrotik.com/product/RB912UAG-2HPnD'
    architecture = 'ar71xx_mikrotik'
    usb = True
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
                '*-ar71xx-mikrotik-nand-large-squashfs-sysupgrade.bin',
                '*-ar71xx-mikrotik-vmlinux-initramfs.elf',
            ]
        }
    }

# Register the Mikrotik RB912 devices.
cgm_base.register_device('lede', MikrotikRB912UAG_2HPnD)
