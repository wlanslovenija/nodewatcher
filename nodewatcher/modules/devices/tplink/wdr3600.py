from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class TPLinkWDR3600v1(cgm_devices.DeviceBase):
    """
    TP-Link WDR3600v1 device descriptor.
    """

    identifier = 'tp-wdr3600v1'
    name = "WDR3600 (v1)"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    usb = True
    radios = [
        cgm_devices.IntegratedRadio('wifi0', "Integrated wireless radio (2.4 GHz)", [
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
        ]),
        cgm_devices.IntegratedRadio('wifi1', "Integrated wireless radio (5 GHz)", [
            cgm_protocols.IEEE80211AN(
                cgm_protocols.IEEE80211AN.SHORT_GI_20,
                cgm_protocols.IEEE80211AN.SHORT_GI_40,
                cgm_protocols.IEEE80211AN.RX_STBC1,
                cgm_protocols.IEEE80211AN.DSSS_CCK_40,
            )
        ], [
            cgm_devices.AntennaConnector('a2', "Antenna1")
        ], [
            cgm_devices.DeviceRadio.MultipleSSID,
        ])
    ]
    switches = [
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=6,
            cpu_port=0,
            cpu_tagged=True,
            vlans=16,
        )
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=2,
            ports=[0, 1],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[0, 2, 3, 4, 5],
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
            'wan0': 'eth0.2',
            'lan0': 'eth0.1',
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
            'wifi1': 'mac80211',
        }
    }
    profiles = {
        'openwrt': {
            # The TLWDR4300 profile is also used for WDR 3600.
            'name': 'TLWDR4300',
            'files': [
                'openwrt-ar71xx-generic-tl-wdr3600-v1-squashfs-factory.bin'
            ]
        }
    }

# Register the TP-Link WDR3600 device.
cgm_base.register_device('openwrt', TPLinkWDR3600v1)
