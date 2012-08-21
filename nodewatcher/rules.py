from registry.rules.scope import *

# Variables
project = value("core.general#project.name")
router = router_descriptor("core.general#platform", "core.general#router")

first_radio = dict(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig", _index = 0)

# Rules
rule(count(router.radios) == 1,
  remove(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig"),
  append(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig",
    wifi_radio = router.radios[0].identifier),

  rule(contains(router.features, "multiple_ssid"),
    remove(_item = "core.interfaces", _cls = "WifiInterfaceConfig", _parent = first_radio),
    append(_item = "core.interfaces", _cls = "WifiInterfaceConfig", _parent = first_radio,
      mode = "ap", essid = "open.wlan-si.net"),
    append(_item = "core.interfaces", _cls = "WifiInterfaceConfig", _parent = first_radio,
      mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "mesh.wlan-si.net",
      routing_protocol = "olsr"),
  ),

  rule(~contains(router.features, "multiple_ssid"),
    remove(_item = "core.interfaces", _cls = "WifiInterfaceConfig", _parent = first_radio),
    append(_item = "core.interfaces", _cls = "WifiInterfaceConfig", _parent = first_radio,
      mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "open.wlan-si.net",
      routing_protocol = "olsr"),
    )
)

rule(count(router.radios) == 0,
   remove(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig")
)
