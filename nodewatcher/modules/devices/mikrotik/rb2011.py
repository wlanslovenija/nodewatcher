from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class MikrotikRB2011UiAS_IN(cgm_devices.DeviceBase):
    """
    Mikrotik RB2011UiAS-IN device descriptor.
    """

    identifier = 'mt-rb2011uias-in'
    name = "RB2011UiAS-IN"
    manufacturer = "MikroTik"
    url = 'http://routerboard.com/RB2011UiAS-IN'
    architecture = 'ar71xx_mikrotik'
    usb = True
    radios = []
    switches = [
        cgm_devices.Switch(
            'sw0', "Gigabit Switch",
            ports=7,
            cpu_port=0,
            cpu_tagged=True,
            vlans=16,
        ),
        cgm_devices.Switch(
            'sw1', "Fast Ethernet Switch",
            ports=6,
            cpu_port=0,
            cpu_tagged=True,
            vlans=16,
        ),
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'wan0', "Wan0",
            switch='sw0',
            vlan=1,
            ports=[0, 1],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=2,
            ports=[0, 2, 3, 4, 5],
        ),
        cgm_devices.SwitchedEthernetPort(
            'lan1', "Lan1",
            switch='sw1',
            vlan=1,
            ports=[0, 1, 2, 3, 4],
        ),
        cgm_devices.SwitchedEthernetPort(
            'sfp0', "SFP",
            switch='sw0',
            vlan=3,
            ports=[0, 6],
        ),
    ]
    antennas = []
    port_map = {
        'openwrt': {
            'sw0': 'switch0',
            'sw1': 'switch1',
            'wan0': 'eth0.1',
            'lan0': 'eth0.2',
            'lan1': 'eth1.1',
            'sfp0': 'eth0.3',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'DefaultNoWifi',
            'files': [
                'openwrt-ar71xx-mikrotik-DefaultNoWifi-rootfs.tar.gz',
                'openwrt-ar71xx-mikrotik-vmlinux-lzma.elf',
                'openwrt-ar71xx-mikrotik-vmlinux-initramfs-lzma.elf',
            ]
        }
    }


class MikrotikRB2011UiAS_2HnD_IN(MikrotikRB2011UiAS_IN):
    """
    Mikrotik RB2011UiAS-2HnD-IN device descriptor.
    """

    identifier = 'mt-rb2011uias-2hnd-in'
    name = "RB2011UiAS-2HnD-IN"
    url = 'http://routerboard.com/RB2011UiAS-2HnD-IN'
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
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211',
        }
    }

# Register the Mikrotik RB2011U devices.
cgm_base.register_device('openwrt', MikrotikRB2011UiAS_IN)
cgm_base.register_device('openwrt', MikrotikRB2011UiAS_2HnD_IN)
