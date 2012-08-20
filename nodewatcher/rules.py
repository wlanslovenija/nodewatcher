from registry.rules.scope import *

# Variables
project = value("core.general#project.name")
router = router_descriptor("core.general#platform", "core.general#router")

# Rules
# TODO this should be on "changed(count(router.radios)); doesn't work because of identifiers
rule(changed("core.general#router"),
  remove(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig"),
  foreach(router.radios,
    append(_item = "core.interfaces", _cls = "WifiRadioDeviceConfig",
      wifi_radio = loop_var().identifier)
  )
)

#rule(contains(router.features, "multiple_ssid"),
#  remove(_item = "core.interfaces", _cls = "WifiInterfaceConfig"),
#  append(_item = "core.interfaces", _cls = "WifiInterfaceConfig",
#    mode = "ap", essid = "open.wlan-si.net"),
#  append(_item = "core.interfaces", _cls = "WifiInterfaceConfig",
#    mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "mesh.wlan-si.net",
#    routing_protocol = "olsr")
#)

#rule(~contains(router.features, "multiple_ssid"),
#  remove(_item = "core.interfaces", _cls = "WifiInterfaceConfig"),
#  append(_item = "core.interfaces", _cls = "WifiInterfaceConfig",
#    mode = "mesh", bssid = "02:CA:FF:EE:BA:BE", essid = "open.wlan-si.net",
#    routing_protocol = "olsr")
#)

