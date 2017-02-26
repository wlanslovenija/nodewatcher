from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices


class MikrotikRB450G(cgm_devices.DeviceBase):
    """
    Mikrotik RB450G device descriptor.
    """

    identifier = 'mt-rb450g'
    name = "RB450G"
    manufacturer = "MikroTik"
    url = 'http://routerboard.com/RB450G'
    architecture = 'ar71xx_mikrotik'
    radios = []
    switches = [
        cgm_devices.Switch(
            'sw0', "Gigabit Switch",
            ports=6,
            cpu_port=0,
            cpu_tagged=True,
            vlans=16,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=1,
                        ports=[0, 1],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=2,
                        ports=[0, 2, 3, 4, 5],
                    ),
                ])
            ]
        ),
    ]
    ports = []
    antennas = []
    port_map = {
        'openwrt': {
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0.{vlan}'),
        }
    }
    profiles = {
        'openwrt': {
            'name': 'DefaultNoWifi',
            'files': [
                '*-ar71xx-mikrotik-DefaultNoWifi-rootfs.tar.gz',
                '*-ar71xx-mikrotik-vmlinux-lzma.elf',
                '*-ar71xx-mikrotik-vmlinux-initramfs-lzma.elf',
            ]
        }
    }

# Register the Mikrotik RB450G device.
cgm_base.register_device('openwrt', MikrotikRB450G)
