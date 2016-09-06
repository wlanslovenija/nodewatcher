from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class IRNASKoruzav2(cgm_devices.DeviceBase):
    """
    IRNAS KORUZAv2 device descriptor.
    """

    identifier = 'irnas-koruzav2'
    name = "KORUZA v2"
    manufacturer = "IRNAS"
    url = 'http://koruza.net'
    architecture = 'ramips_mt7621'
    usb = True
    radios = [
        # TODO: Change this for production KORUZA version.
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio (5 GHz)", [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_20,
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
                cgm_protocols.IEEE80211AN.RX_STBC1,
                cgm_protocols.IEEE80211AN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a1', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ]),
        cgm_devices.IntegratedRadio('wifi1', "Integrated wireless radio (2.4 GHz)", [
            cgm_protocols.IEEE80211BGN(
                cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                cgm_protocols.IEEE80211BGN.RX_STBC1,
                cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a2', "Antenna0")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[0, 1, 2, 3, 4, 6],
            cpu_port=6,
            cpu_tagged=True,
            vlans=16,
        )
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=2,
            ports=[4, 6],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[0, 1, 2, 3, 6],
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
        ),
        cgm_devices.InternalAntenna(
            identifier='a2',
            polarization='horizontal',
            angle_horizontal=360,
            angle_vertical=75,
            gain=2,
        )
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'wifi1': 'radio1',
            'sw0': 'switch0',
            'lan0': 'eth0.1',
            'wan0': 'eth0.2',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
            'wifi1': 'mac80211'
        }
    }
    profiles = {
        # TODO: Use KORUZA-specific profile for production KORUZA version.
        'openwrt': {
            'name': 'WITI',
            'files': [
                'openwrt-ramips-mt7621-witi-squashfs-sysupgrade.bin'
            ]
        }
    }

    @cgm_devices.register_module('openwrt')
    def openwrt_usb_wifi_packages(node, cfg):
        """
        Include packages needed for the USB wifi radio bundled with KORUZA.
        """

        cfg.packages.update([
            'kmod-rt2800-lib',
            'kmod-rt2800-usb',
            'kmod-rt2x00-lib',
            'kmod-rt2x00-usb'
        ])

    @cgm_devices.register_module('openwrt')
    def openwrt_disable_rtc_pcf8563(node, cfg):
        """
        Disable the kmod-rtc-pcf8563 package as it interferes with SFP due
        to it having the same address on the I2C bus.
        """

        cfg.packages.add('-kmod-rtc-pcf8563')

# Register the IRNAS KORUZA device.
cgm_base.register_device('openwrt', IRNASKoruzav2)
