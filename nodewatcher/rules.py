from registry.rules.scope import *

# Variables
project = value("core.general#project.name")
router = router_descriptor("core.general#platform", "core.general#router")

first_radio = dict(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig", _index = 0)

# Rules
rule(count(router.radios) == 1,
  remove("core.interfaces", "WifiRadioDeviceConfig"),
  append("core.interfaces", "WifiRadioDeviceConfig",
    wifi_radio = router.radios[0].identifier),

  rule(contains(router.features, "multiple_ssid"),
    remove("core.interfaces", "WifiInterfaceConfig", first_radio),
    append("core.interfaces", "WifiInterfaceConfig", first_radio,
      mode = "ap", essid = "open.wlan-si.net"),
    append("core.interfaces", "WifiInterfaceConfig", first_radio,
      mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "mesh.wlan-si.net",
      routing_protocol = "olsr"),
  ),

  rule(~contains(router.features, "multiple_ssid"),
    remove("core.interfaces", "WifiInterfaceConfig", first_radio),
    append("core.interfaces", "WifiInterfaceConfig", first_radio,
      mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "open.wlan-si.net",
      routing_protocol = "olsr"),
    )
)

rule(count(router.radios) == 0,
  remove("core.interfaces", "WifiRadioDeviceConfig")
)
