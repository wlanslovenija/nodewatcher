from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTNano(cgm_devices.DeviceBase):
    """
    UBNT Nano device descriptor.
    """

    identifier = 'ub-nano'
    name = "Nano"
    manufacturer = "Ubiquity"
    url = 'http://www.ubnt.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Wifi0", [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
                cgm_protocols.IEEE80211AN.TX_STBC1,
                cgm_protocols.IEEE80211AN.RX_STBC1,
                cgm_protocols.IEEE80211AN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = []
    ports = [
        cgm_devices.EthernetPort('lan0', "Lan0")
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
            'name': 'UBNT',
            'files': [
                'openwrt-ar71xx-generic-ubnt-nano-m-squashfs-factory.bin'
            ]
        }
    }


class UBNTNanoM5(UBNTNano):
    """
    UBNT Nano M5 device descriptor.
    """

    identifier = 'ub-nano-m5'
    name = "Nano M5"


class UBNTNanoM5XW(UBNTNano):
    """
    UBNT Nano M5 XW device descriptor.
    """

    identifier = 'ub-nano-m5-xw'
    name = "Nano M5 XW"
    profiles = {
        'openwrt': {
            'name': 'UBNT',
            'files': [
                'openwrt-ar71xx-generic-ubnt-nano-m-xw-squashfs-factory.bin'
            ]
        }
    }

# Register the UBNT Nano device
cgm_base.register_device('openwrt', UBNTNano)
cgm_base.register_device('openwrt', UBNTNanoM5)
cgm_base.register_device('openwrt', UBNTNanoM5XW)
