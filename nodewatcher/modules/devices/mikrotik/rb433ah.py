from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRB433AH(cgm_devices.DeviceBase):
    """
    Mikrotik RB433AH device descriptor.
    """

    identifier = 'rb433ah'
    name = "RB433AH"
    manufacturer = "MikroTik"
    url = 'http://routerboard.com/RB433AH'
    architecture = 'ar71xx'
    radios = [
        # TODO: This information is not correct, there are no integrated radios
        cgm_devices.IntegratedRadio('wifi0', "Wifi0", [cgm_protocols.IEEE80211BG], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = [
        # TODO: This information is possibly not correct
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=5,
            cpu_port=0,
            vlans=16,
        )
    ]
    ports = [
        # TODO: This information is possibly not correct
        cgm_devices.EthernetPort('wan0', "Wan0"),
        cgm_devices.EthernetPort('lan0', "Lan0"),
    ]
    antennas = [
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
        Network configuration CGM for Mikrotik RB433AH.
        """

        pass

# Register the Mikrotik RB433AH device
cgm_base.register_device('openwrt', MikrotikRB433AH)
