from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class BuffaloWHR_HP_G54(cgm_devices.DeviceBase):
    """
    Buffalo WHR-HP-G54 device descriptor.
    """

    identifier = 'whr-hp-g54'
    name = "WHR-HP-G54"
    manufacturer = "Buffalo Technology Ltd."
    url = 'http://www.buffalo-technology.com/'
    architecture = 'brcm47xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Wifi0", [cgm_protocols.IEEE80211BG], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=5,
            cpu_port=0,
            vlans=16,
        )
    ]
    ports = [
        cgm_devices.EthernetPort('wan0', "Wan0"),
        cgm_devices.EthernetPort('lan0', "Lan0"),
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
            'wifi0': 'wlan0',
            'sw0': 'eth0',
            'wan0': 'eth1',
            'lan0': 'eth0',
        }
    }

    @cgm_devices.register_module()
    def network(node, cfg):
        """
        Network configuration CGM for Buffalo WHR-HP-G54.
        """

        pass

# Register the Buffalo WHR-HP-G54 device
cgm_base.register_device('openwrt', BuffaloWHR_HP_G54)
