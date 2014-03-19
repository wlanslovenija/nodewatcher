from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class TPLinkWR1043NDv1(cgm_devices.DeviceBase):
    """
    TP-Link WR1043NDv1 device descriptor.
    """

    identifier = 'tp-wr1043ndv1'
    name = "WR1043ND (v1)"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Wifi0", [
            cgm_protocols.IEEE80211N(
                cgm_protocols.IEEE80211N.SHORT_GI_20,
                cgm_protocols.IEEE80211N.SHORT_GI_40,
                cgm_protocols.IEEE80211N.RX_STBC1,
                cgm_protocols.IEEE80211N.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[0, 1, 2, 3, 4, 5],
            cpu_port=5,
            vlans=16,
        )
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=2,
            ports=[0, 5],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[1, 2, 3, 4, 5],
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
    features = [
        cgm_devices.Features.MultipleSSID,
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'sw0': 'rtl8366rb',
            'wan0': 'eth0.2',
            'lan0': 'eth0.1',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR1043',
            'files': [
                'openwrt-ar71xx-generic-tl-wr1043nd-v1-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR1043NDv2(TPLinkWR1043NDv1):
    """
    TP-Link WR1043NDv2 device descriptor.
    """

    identifier = 'tp-wr1043ndv2'
    name = "WR1043ND (v2)"
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
            'name': 'TLWR1043',
            'files': [
                'openwrt-ar71xx-generic-tl-wr1043nd-v2-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link WR1043ND device
cgm_base.register_device('openwrt', TPLinkWR1043NDv1)
cgm_base.register_device('openwrt', TPLinkWR1043NDv2)
