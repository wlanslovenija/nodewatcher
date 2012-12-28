from nodewatcher.core.registry.cgm import base as cgm_base, protocols as cgm_protocols, routers as cgm_routers

class AsusWL500GPremiumV1(cgm_routers.RouterBase):
    """
    Asus WL500G Premium v1 device descriptor.
    """
    identifier = "wl500gpv1"
    name = "WL500G Premium v1"
    manufacturer = "Asus"
    url = "http://www.asus.com/"
    architecture = "brcm47xx"
    radios = [
      cgm_routers.IntegratedRadio("wifi0", "Wifi0", [cgm_protocols.IEEE80211BG], [
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
    port_map = {
      "openwrt": {
        "wifi0" : "wlan0",
        "wan0"  : "eth1",
        "lan0"  : "eth0",
      }
    }

    @cgm_routers.register_module()
    def network(node, cfg):
        """
        Network configuration CGM for Asus WL500G Premium v1.
        """
        pass

# Register the Asus WL500G Premium v1 router
cgm_base.register_router("openwrt", AsusWL500GPremiumV1)
