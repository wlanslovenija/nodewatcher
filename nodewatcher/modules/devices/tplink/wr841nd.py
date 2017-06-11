from django.utils.translation import ugettext_lazy as _

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
        cgm_devices.IntegratedRadio('wifi0', _("Integrated wireless radio"), [
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
                '*-ar71xx-generic-tl-wr841*-v1.5-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v1.5-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v1.5',
            'files': [
                '*-ar71xx-generic-tl-wr841-v1.5-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v1.5-squashfs-sysupgrade.bin',
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
                '*-ar71xx-generic-tl-wr841*-v3-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v3-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v3',
            'files': [
                '*-ar71xx-generic-tl-wr841-v3-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v3-squashfs-sysupgrade.bin',
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
                '*-ar71xx-generic-tl-wr841*-v5-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v5-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v5',
            'files': [
                '*-ar71xx-generic-tl-wr841-v5-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v5-squashfs-sysupgrade.bin',
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
            vlans=1,
            presets=[
                cgm_devices.SwitchPreset('default', _("Default VLAN configuration"), vlans=[
                    cgm_devices.SwitchVLANPreset(
                        'lan0', "Lan0",
                        vlan=1,
                        ports=[0, 1, 2, 3, 4],
                    )
                ])
            ]
        )
    ]
    ports = [
        cgm_devices.EthernetPort('wan0', "Wan0"),
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0'),
            'wan0': 'eth1',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                '*-ar71xx-generic-tl-wr841*-v7-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v7-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v7',
            'files': [
                '*-ar71xx-generic-tl-wr841-v7-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v7-squashfs-sysupgrade.bin',
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
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth1'),
            'wan0': 'eth0',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                '*-ar71xx-generic-tl-wr841*-v8-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v8-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v8',
            'files': [
                '*-ar71xx-generic-tl-wr841-v8-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v8-squashfs-sysupgrade.bin',
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
                '*-ar71xx-generic-tl-wr841*-v9-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v9-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v9',
            'files': [
                '*-ar71xx-generic-tl-wr841-v9-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v9-squashfs-sysupgrade.bin',
            ]
        }
    }


class TPLinkWR841NDv10(TPLinkWR841NDv7):
    """
    TP-Link WR841NDv10 device descriptor.
    """

    identifier = 'tp-wr841ndv10'
    name = "WR841ND (v10)"
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                '*-ar71xx-generic-tl-wr841*-v10-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v10-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v10',
            'files': [
                '*-ar71xx-generic-tl-wr841-v10-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v10-squashfs-sysupgrade.bin',
            ]
        }
    }


class TPLinkWR841NDv11(TPLinkWR841NDv7):
    """
    TP-Link WR841NDv11 device descriptor.
    """

    identifier = 'tp-wr841ndv11'
    name = "WR841ND (v11)"
    profiles = {
        'openwrt': {
            'name': 'TLWR841',
            'files': [
                '*-ar71xx-generic-tl-wr841*-v11-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841*-v11-squashfs-sysupgrade.bin',
            ]
        },
        'lede': {
            'name': 'tl-wr841-v11',
            'files': [
                '*-ar71xx-generic-tl-wr841-v11-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v11-squashfs-sysupgrade.bin',
            ]
        }
    }


class TPLinkWR841NDv12(TPLinkWR841NDv7):
    """
    TP-Link WR841NDv12 device descriptor.
    """

    identifier = 'tp-wr841ndv12'
    name = "WR841ND (v12)"
    profiles = {
        'lede': {
            'name': 'tl-wr841-v12',
            'files': [
                '*-ar71xx-generic-tl-wr841-v12-squashfs-factory.bin',
                '*-ar71xx-generic-tl-wr841-v12-squashfs-sysupgrade.bin',
            ]
        }
    }

# Register the TP-Link WR841ND device.
cgm_base.register_device('openwrt', TPLinkWR841NDv1)
cgm_base.register_device('openwrt', TPLinkWR841NDv3)
cgm_base.register_device('openwrt', TPLinkWR841NDv5)
cgm_base.register_device('openwrt', TPLinkWR841NDv7)
cgm_base.register_device('openwrt', TPLinkWR841NDv8)
cgm_base.register_device('openwrt', TPLinkWR841NDv9)
cgm_base.register_device('openwrt', TPLinkWR841NDv10)
cgm_base.register_device('openwrt', TPLinkWR841NDv11)
cgm_base.register_device('lede', TPLinkWR841NDv12)
