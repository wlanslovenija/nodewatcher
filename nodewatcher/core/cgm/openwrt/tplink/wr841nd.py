from nodewatcher.registry.cgm import base as cgm_base
from nodewatcher.registry.cgm import routers as cgm_routers
from nodewatcher.registry.cgm import protocols as cgm_protocols

class TPLinkWR841ND(cgm_routers.RouterBase):
    """
    TP-Link WR841ND device descriptor.
    """
    identifier = "wr841nd"
    name = "WR841ND"
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

# Register the TP-Link WR841ND router
cgm_base.register_router("openwrt", TPLinkWR841ND)
