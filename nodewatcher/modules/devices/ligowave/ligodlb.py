from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class LigoWaveLigoDLB5(cgm_devices.DeviceBase):
    """
    LigoWave LigoDLB 5 device descriptor.
    """

    identifier = 'lw-ligodlb-5'
    name = "LigoDLB 5"
    manufacturer = "LigoWave"
    url = 'https://www.ligowave.com/'
    architecture = 'ar71xx'
    usb = True
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio", [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_20,
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
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
        # TODO: This information is probably not correct.
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
            'wifi0': 'mac80211',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'DELIBERANT',
            'files': [
                'openwrt-ar71xx-generic-deliberant-squashfs-sysupgrade.bin',
            ],
        }
    }


class LigoWaveLigoDLB5_90(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-5-90'
    name = 'LigoDLB 5-90'


class LigoWaveLigoDLB5_15(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-5-15'
    name = 'LigoDLB 5-15'


class LigoWaveLigoDLB5_15B(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-5-15b'
    name = 'LigoDLB 5-15B'


class LigoWaveLigoDLB5_20(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-5-20'
    name = 'LigoDLB 5-20'


class LigoWaveLigoDLB_Mach5(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-m5'
    name = 'LigoDLB MACH 5'


class LigoWaveLigoDLB_Echo5(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-e5'
    name = 'LigoDLB ECHO 5'


class LigoWaveLigoDLB_Echo5D(LigoWaveLigoDLB5):
    identifier = 'lw-ligodlb-e5d'
    name = 'LigoDLB ECHO 5D'


class LigoWaveLigoDLB2(LigoWaveLigoDLB5):
    """
    LigoWave LigoDLB 2 device descriptor.
    """

    identifier = 'lw-ligodlb-2'
    name = 'LigoDLB 2'
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


class LigoWaveLigoDLB2_90(LigoWaveLigoDLB2):
    identifier = 'lw-ligodlb-2-90'
    name = 'LigoDLB 2-90'


class LigoWaveLigoDLB2_9(LigoWaveLigoDLB2):
    identifier = 'lw-ligodlb-2-9'
    name = 'LigoDLB 2-9'


class LigoWaveLigoDLB2_9B(LigoWaveLigoDLB2):
    identifier = 'lw-ligodlb-2-9b'
    name = 'LigoDLB 2-9B'


class LigoWaveLigoDLB2_14(LigoWaveLigoDLB2):
    identifier = 'lw-ligodlb-2-14'
    name = 'LigoDLB 2-14'

# Register the LigoDLB devices.
cgm_base.register_device('openwrt', LigoWaveLigoDLB5)
cgm_base.register_device('openwrt', LigoWaveLigoDLB5_90)
cgm_base.register_device('openwrt', LigoWaveLigoDLB5_15)
cgm_base.register_device('openwrt', LigoWaveLigoDLB5_15B)
cgm_base.register_device('openwrt', LigoWaveLigoDLB5_20)
cgm_base.register_device('openwrt', LigoWaveLigoDLB_Mach5)
cgm_base.register_device('openwrt', LigoWaveLigoDLB_Echo5)
cgm_base.register_device('openwrt', LigoWaveLigoDLB_Echo5D)
cgm_base.register_device('openwrt', LigoWaveLigoDLB2)
cgm_base.register_device('openwrt', LigoWaveLigoDLB2_90)
cgm_base.register_device('openwrt', LigoWaveLigoDLB2_9)
cgm_base.register_device('openwrt', LigoWaveLigoDLB2_9B)
cgm_base.register_device('openwrt', LigoWaveLigoDLB2_14)
