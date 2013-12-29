from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, routers as cgm_routers


class Fonera(cgm_routers.DeviceBase):
    """
    Fonera FON-2100 device descriptor.
    """

    identifier = 'fon-2100'
    name = "Fonera"
    manufacturer = "Fon Wireless Ltd."
    url = 'http://www.fon.com'
    architecture = 'atheros'
    radios = [
        cgm_routers.IntegratedRadio('wifi0', "Wifi0", [cgm_protocols.IEEE80211BG], [
            cgm_routers.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = []
    ports = [
        cgm_routers.EthernetPort('wan0', "Ethernet0")
    ]
    antennas = [
        cgm_routers.InternalAntenna(
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

    @cgm_routers.register_module()
    def network(node, cfg):
        """
        Network configuration CGM for FON-2100.
        """

        pass

# Register the FON-2100 router
cgm_base.register_router('openwrt', Fonera)
