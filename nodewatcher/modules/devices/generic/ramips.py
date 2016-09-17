from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class GenericRamipsA5V11(cgm_devices.DeviceBase):
    """
    A5-V11 device descriptor.
    """

    identifier = 'generic-ramips-a5-v11'
    name = "A5-V11"
    manufacturer = "Generic"
    url = 'https://wiki.openwrt.org/toh/unbranded/a5-v11'
    architecture = 'ramips_rt305x'
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
        cgm_devices.Switch(
            'sw0', "Switch0",
            ports=[0, 6],
            cpu_port=6,
            cpu_tagged=True,
            vlans=16,
        )
    ]
    ports = [
        cgm_devices.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[0, 6],
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
            'sw0': cgm_devices.SwitchPortMap('switch0', vlans='eth0.{vlan}'),
        }
    }
    drivers = {
        'openwrt': {
            'wifi0': 'mac80211'
        }
    }
    profiles = {
        'openwrt': {
            'name': 'A5-V11',
            'files': [
                'openwrt-ramips-rt305x-a5-v11-squashfs-factory.bin'
            ]
        }
    }

# Register the Generic Ramips devices.
cgm_base.register_device('openwrt', GenericRamipsA5V11)
