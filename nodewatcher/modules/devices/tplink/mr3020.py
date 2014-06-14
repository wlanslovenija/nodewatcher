from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class TPLinkMR3020v1(cgm_devices.DeviceBase):
    """
    TP-Link MR3020v1 device descriptor.
    """

    identifier = 'tp-mr3020v1'
    name = "MR3020 (v1)"
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
    ]
    ports = [
        cgm_devices.EthernetPort('wan0', "Wan0"),
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
            'wan0': 'eth0',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'TLMR3020',
            'files': [
                'openwrt-ar71xx-generic-tl-mr3020-v1-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link MR3020 device
cgm_base.register_device('openwrt', TPLinkMR3020v1)
