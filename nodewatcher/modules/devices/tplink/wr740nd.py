from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class TPLinkWR740NDv1(cgm_devices.DeviceBase):
    """
    TP-Link WR740NDv1 device descriptor.
    """

    identifier = 'tp-wr740ndv1'
    name = "WR740ND (v1)"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Wifi0", [
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
            'wan0': 'eth1',
            'lan0': 'eth0',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLWR740',
            'files': [
                'openwrt-ar71xx-generic-tl-wr740n-v1-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR740NDv3(TPLinkWR740NDv1):
    """
    TP-Link WR740NDv3 device descriptor.
    """

    identifier = 'tp-wr740ndv3'
    name = "WR740ND (v3)"
    profiles = {
        'openwrt': {
            'name': 'TLWR740',
            'files': [
                'openwrt-ar71xx-generic-tl-wr740n-v3-squashfs-factory.bin'
            ]
        }
    }


class TPLinkWR740NDv4(TPLinkWR740NDv1):
    """
    TP-Link WR740NDv4 device descriptor.
    """

    identifier = 'tp-wr740ndv4'
    name = "WR740ND (v4)"
    profiles = {
        'openwrt': {
            'name': 'TLWR740',
            'files': [
                'openwrt-ar71xx-generic-tl-wr740n-v4-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link WR740ND device
cgm_base.register_device('openwrt', TPLinkWR740NDv1)
cgm_base.register_device('openwrt', TPLinkWR740NDv3)
cgm_base.register_device('openwrt', TPLinkWR740NDv4)
