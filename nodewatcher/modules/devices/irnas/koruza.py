from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices


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
        # TODO: Change index for production KORUZA version.
        cgm_devices.USBRadio('wifi-usb0', "USB wireless radio", index=2)
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
            'sw0': 'switch0',
            'lan0': 'eth0.1',
            'wan0': 'eth0.2',
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

# Register the IRNAS KORUZA device.
cgm_base.register_device('openwrt', IRNASKoruzav2)
