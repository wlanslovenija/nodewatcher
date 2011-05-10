from registry.cgm import base as cgm_base

# Register the FON-2100 router
cgm_base.register_router_model("openwrt",
  model = "fon-2100",
  name = "Fonera",
  architecture = "atheros",
  supported_radios = 1
)

# Register all special submodules for this router
# import core.cgm.openwrt.fon2100.fubar

