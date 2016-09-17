from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class LinksysWRT54GL(cgm_devices.DeviceBase):
    """
    Linksys WRT54GL device descriptor.
    """

    identifier = 'wrt54gl'
    name = "WRT54GL"
    manufacturer = "Linksys"
    url = 'http://www.linksysbycisco.com/'
    architecture = 'brcm47xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [cgm_protocols.IEEE80211BG], [
            cgm_devices.AntennaConnector('a1', "Antenna0"),
            cgm_devices.AntennaConnector('a2', "Antenna1"),
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=6,
            cpu_port=5,
            vlans=16,
            configurable=False,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'wan0', "Wan0",
                        vlan=2,
                        ports=[5, 0],
                    ),
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=1,
                        ports=[5, 1, 2, 3, 4],
                    ),
                ])
            ]
        )
    ]
    ports = []
    antennas = [
        # TODO: this information is probably not correct
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
            'wifi0': 'wlan0',
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0.{vlan}'),
        }
    }

# Register the Linksys WRT54GL device.
cgm_base.register_device('openwrt', LinksysWRT54GL)
