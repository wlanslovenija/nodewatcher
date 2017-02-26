from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class SiemensSX763v2(cgm_devices.DeviceBase):
    """
    Siemens SX763v2 device descriptor.
    """

    identifier = 'sm-sx763v2'
    name = "SX763 (v2)"
    manufacturer = "Siemens"
    url = 'http://www.siemens.com/'
    architecture = 'lantiq'
    usb = True
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
            cgm_protocols.IEEE80211BG()
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[1, 2, 3, 4, 5],
            cpu_port=5,
            vlans=16,
            cpu_tagged=True,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=1,
                        ports=[1, 5],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=2,
                        ports=[2, 3, 4, 5],
                    )
                ])
            ]
        )
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
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'GIGASX76X',
            'files': [
                '*-lantiq-xway-GIGASX76X-squashfs.image',
            ]
        }
    }

    @cgm_devices.register_module(platform='openwrt', weight=15)
    def configure_mac(node, cfg):
        """
        Configures MAC addresses that need to be loaded from flash.
        """

        lan_mac = cfg.maccfg.add(mac='lan0')
        lan_mac.source = 'mtd-ascii'
        lan_mac.args = 'uboot_env ethaddr'

        wan_mac = cfg.maccfg.add(mac='wan0')
        wan_mac.source = 'mtd-ascii'
        wan_mac.args = 'uboot_env ethaddr'
        wan_mac.offset = 1

        cfg.packages.add('maccfg')

# Register the Siemens SX763 device
cgm_base.register_device('openwrt', SiemensSX763v2)
