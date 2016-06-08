from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class GLiNet6408Av1(cgm_devices.DeviceBase):
    """
    GL.iNet 6408A v1 device descriptor.
    """

    identifier = 'gl-inet6408av1'
    name = "GL.iNet 6408A (v1)"
    manufacturer = "GL Technologies"
    url = 'http://www.gl-inet.com/'
    architecture = 'ar71xx'
    usb = True
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
    switches = [
    ]
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
            'wan0': 'eth0',
            'lan0': 'eth1',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'GLINET',
            'files': [
                'openwrt-ar71xx-generic-gl-inet-6408A-v1-squashfs-factory.bin',
                'openwrt-ar71xx-generic-gl-inet-6408A-v1-squashfs-sysupgrade.bin'
            ]
        }
    }


class GLiNet6416Av1(GLiNet6408Av1):
    """
    GL.iNet 6416A v1 device descriptor.
    """

    identifier = 'gl-inet6416av1'
    name = "GL.iNet 6416A (v1)"
    profiles = {
        'openwrt': {
            'name': 'GLINET',
            'files': [
                'openwrt-ar71xx-generic-gl-inet-6416A-v1-squashfs-factory.bin',
                'openwrt-ar71xx-generic-gl-inet-6416A-v1-squashfs-sysupgrade.bin'
            ]
        }
    }

# Register the GL.iNet devices.
cgm_base.register_device('openwrt', GLiNet6408Av1)
cgm_base.register_device('openwrt', GLiNet6416Av1)
