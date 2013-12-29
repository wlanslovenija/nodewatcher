from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, routers as cgm_routers


class SiemensSX763v2(cgm_routers.DeviceBase):
    """
    Siemens SX763v2 device descriptor.
    """

    identifier = 'sm-sx763v2'
    name = "SX763 (v2)"
    manufacturer = "Siemens"
    url = 'http://www.siemens.com/'
    architecture = 'lantiq'
    radios = [
        cgm_routers.IntegratedRadio('wifi0', "Wifi0", [
            cgm_protocols.IEEE80211BG()
        ], [
            cgm_routers.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = [
        cgm_routers.Switch(
            'sw0', "Switch0",
            ports=[1, 2, 3, 4, 5],
            cpu_port=5,
            vlans=16,
        )
    ]
    ports = [
        cgm_routers.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=1,
            ports=[1, 5],
        ),
        cgm_routers.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=2,
            ports=[2, 3, 4, 5],
        )
    ]
    antennas = [
        # TODO: This information is probably not correct
        cgm_routers.InternalAntenna(
            identifier='a1',
            polarization='horizontal',
            angle_horizontal=360,
            angle_vertical=75,
            gain=2,
        )
    ]
    features = [
        cgm_routers.Features.MultipleSSID,
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
                'openwrt-lantiq-danube-GIGASX76X-squashfs.image',
            ]
        }
    }

# Register the Siemens SX763 router
cgm_base.register_device('openwrt', SiemensSX763v2)
