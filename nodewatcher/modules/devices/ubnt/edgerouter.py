from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTEdgerouterX(cgm_devices.DeviceBase):
    """
    UBNT EdgerouterX device descriptor.
    """

    identifier = 'ub-edgerouter-x'
    name = "Edgerouter X"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ramips_mt7621'
    radios = []
    switches = [
        cgm_devices.Switch(
            'sw0', "Gigabit switch",
            ports=[0, 1, 2, 3, 4, 6],
            cpu_port=6,
            cpu_tagged=True,
            vlans=16,
            configurable=True,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=2,
                        ports=[0, 6],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=1,
                        ports=[1, 2, 3, 4, 6],
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
        'lede': {
            'name': 'ubnt-erx',
            'files': [
                '*-ramips-mt7621-ubnt-erx-squashfs-sysupgrade.tar',
            ]
        }
    }

# Register Edgerouter X device.
cgm_base.register_device('lede', UBNTEdgerouterX)
