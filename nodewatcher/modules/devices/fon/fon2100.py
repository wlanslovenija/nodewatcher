from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class Fonera(cgm_devices.DeviceBase):
    """
    Fonera FON-2100 device descriptor.
    """

    identifier = 'fon-2100'
    name = "Fonera"
    manufacturer = "Fon Wireless Ltd."
    url = 'http://www.fon.com'
    architecture = 'atheros'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio", [cgm_protocols.IEEE80211BG], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('wan0', "Ethernet0")
    ]
    antennas = [
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
            'wan0': 'eth0',
        }
    }

    @cgm_devices.register_module()
    def network(node, cfg):
        """
        Network configuration CGM for FON-2100.
        """

        pass

# Register the FON-2100 device
cgm_base.register_device('openwrt', Fonera)
