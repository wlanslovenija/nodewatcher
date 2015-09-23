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
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio", [
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
        )
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=1,
            ports=[1, 5],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=2,
            ports=[2, 3, 4, 5],
        )
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
            'sw0': 'eth0',
            'wan0': 'eth0.1',
            'lan0': 'eth0.2',
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
                'openwrt-lantiq-xway-GIGASX76X-squashfs.image',
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
