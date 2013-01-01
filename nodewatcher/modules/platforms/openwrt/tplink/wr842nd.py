from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, routers as cgm_routers

class TPLinkWR842ND(cgm_routers.RouterBase):
    """
    TP-Link WR842ND device descriptor.
    """
    identifier = "wr842nd"
    name = "WR842ND"
    manufacturer = "TP-Link"
    url = "http://www.tp-link.com/"
    architecture = "ar71xx"
    radios = [
      cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG, cgm_protocols.IEEE80211N], [
        cgm_routers.AntennaConnector("a1", "Antenna0")
      ])
    ]
    ports = [
      cgm_routers.EthernetPort("wan0", "Wan0"),
      cgm_routers.EthernetPort("lan0", "Lan0")
    ]
    antennas = [
      # TODO this information is probably not correct
      cgm_routers.InternalAntenna(
        identifier = "a1",
        polarization = "horizontal",
        angle_horizontal = 360,
        angle_vertical = 75,
        gain = 2
      )
    ]
    features = [
      cgm_routers.Features.MultipleSSID,
    ]
    port_map = {
      "openwrt": {
        "wifi0" : "radio0",
        "wan0"  : "eth1",
        "lan0"  : "eth0",
      }
    }

# Register the TP-Link WR842ND router
cgm_base.register_router("openwrt", TPLinkWR842ND)
