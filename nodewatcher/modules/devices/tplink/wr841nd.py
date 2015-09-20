from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class TPLinkWR841NDv1(cgm_devices.DeviceBase):
    """
    TP-Link WR841NDv1 device descriptor.
    """

    identifier = 'tp-wr841ndv1'
    name = "WR841ND (v1)"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio", [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = []
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
            'wifi0': 'radio0',
            'sw0': 'switch0',
            'wan0': 'wan',
            'lan0': ['lan1', 'lan2', 'lan3', 'lan4'],
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841nd-v1.5-squashfs-factory.bin'
            ]
        }
    }

    @cgm_devices.register_module(platform='openwrt', weight=16)
    def configure_network(node, cfg):
        """
        Configures device-specific networking.
        """

        mac = cfg.network.add(interface='mac0')
        mac.ifname = 'eth0'
        mac.proto = 'none'


class TPLinkWR841NDv3(TPLinkWR841NDv1):
    """
    TP-Link WR841NDv3 device descriptor.
    """

    identifier = 'tp-wr841ndv3'
    name = "WR841ND (v3)"
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841nd-v3-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR841NDv5(TPLinkWR841NDv1):
    """
    TP-Link WR841NDv5 device descriptor.
    """

    identifier = 'tp-wr841ndv5'
    name = "WR841ND (v5)"
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841nd-v5-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR841NDv7(TPLinkWR841NDv1):
    """
    TP-Link WR841NDv7 device descriptor.
    """

    identifier = 'tp-wr841ndv7'
    name = "WR841ND (v7)"
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
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[0, 1, 2, 3, 4],
        )
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'sw0': 'switch0',
            'wan0': 'eth1',
            'lan0': 'eth0',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841nd-v7-squashfs-factory.bin'
            ]
        }
    }

    # Do not inherit network configuration
    configure_network = None


class TPLinkWR841NDv8(TPLinkWR841NDv7):
    """
    TP-Link WR841NDv8 device descriptor.
    """

    identifier = 'tp-wr841ndv8'
    name = "WR841ND (v8)"
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'sw0': 'switch0',
            'wan0': 'eth0',
            'lan0': 'eth1',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841n-v8-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR841NDv9(TPLinkWR841NDv7):
    """
    TP-Link WR841NDv9 device descriptor.
    """

    identifier = 'tp-wr841ndv9'
    name = "WR841ND (v9)"
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                'openwrt-ar71xx-generic-tl-wr841n-v9-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link WR841ND device
cgm_base.register_device('openwrt', TPLinkWR841NDv1)
cgm_base.register_device('openwrt', TPLinkWR841NDv3)
cgm_base.register_device('openwrt', TPLinkWR841NDv5)
cgm_base.register_device('openwrt', TPLinkWR841NDv7)
cgm_base.register_device('openwrt', TPLinkWR841NDv8)
cgm_base.register_device('openwrt', TPLinkWR841NDv9)
