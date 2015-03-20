from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTBullet(cgm_devices.DeviceBase):
    """
    UBNT Bullet device descriptor.
    """

    identifier = 'ub-bullet'
    name = "Bullet"
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
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
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
                'openwrt-ar71xx-generic-ubnt-bullet-m-squashfs-factory.bin',
                'openwrt-ar71xx-generic-ubnt-bullet-m-squashfs-sysupgrade.bin',
            ]
        }
    }


class UBNTBulletM5(UBNTBullet):
    """
    UBNT Bullet M5 device descriptor.
    """

    identifier = 'ub-bullet-m5'
    name = "Bullet M5"

# Register the UBNT Bullet device
cgm_base.register_device('openwrt', UBNTBullet)
cgm_base.register_device('openwrt', UBNTBulletM5)
