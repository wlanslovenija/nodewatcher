from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, routers as cgm_routers


class TPLinkWR703N(cgm_routers.RouterBase):
    """
    TP-Link WR703N device descriptor.
    """

    identifier = 'tp-wr703n'
    name = "WR703N"
    manufacturer = "TP-Link"
    url = 'http://www.tp-link.com/'
    architecture = 'ar71xx'
    radios = [
        cgm_routers.IntegratedRadio('wifi0', "Wifi0", [
            cgm_protocols.IEEE80211N(
                cgm_protocols.IEEE80211N.SHORT_GI_20,
                cgm_protocols.IEEE80211N.SHORT_GI_40,
                cgm_protocols.IEEE80211N.RX_STBC1,
                cgm_protocols.IEEE80211N.DSSS_CCK_40,
            )
        ], [
            cgm_routers.AntennaConnector('a1', "Antenna0")
        ])
    ]
    switches = [
        cgm_routers.Switch(
            'sw0', "Switch0",
            ports=5,
            cpu_port=0,
            vlans=16,
        )
    ]
    ports = [
        cgm_routers.EthernetPort('wan0', "Wan0"),
        cgm_routers.SwitchedEthernetPort(
            'lan0', "Lan0",
            switch='sw0',
            vlan=1,
            ports=[0, 1, 2, 3, 4],
        )
    ]
    antennas = [
        # TODO: This information is probably not correct
        cgm_routers.InternalAntenna(
            identifier='a1',
            polarization='horizontal',
            angle_horizontal=360,
            angle_vertical=75,
            gain=2,
        )
    ]
    features = [
        cgm_routers.Features.MultipleSSID,
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'radio0',
            'sw0': 'eth0',
            'wan0': 'eth1',
            'lan0': 'eth0',
        }
    }

# Register the TP-Link WR703N router
cgm_base.register_router('openwrt', TPLinkWR703N)
