from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRBmAP2nD(cgm_devices.DeviceBase):
    """
    Mikrotik RB mAP 2nD (mAP) device descriptor.
    """

    identifier = 'mt-rbmap-2nd'
    name = "mAP (RBmAP2nD)"
    manufacturer = "MikroTik"
    url = 'https://mikrotik.com/product/RBmAP2nD'
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
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[0, 1, 2],
            cpu_port=0,
            cpu_tagged=True,
            vlans=4096,
            configurable=True,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=2,
                        ports=[0, 1],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=1,
                        ports=[0, 2],
                    ),
                ])
            ]
        ),
    ]
    ports = []
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
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0.{vlan}'),
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
                '*-ar71xx-mikrotik-vmlinux-initramfs.elf',
            ]
        }
    }

# Register the Mikrotik mAP devices.
cgm_base.register_device('lede', MikrotikRBmAP2nD)
