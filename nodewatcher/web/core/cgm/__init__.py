from web.registry import registration
from web.registry import forms as registry_forms
from web.registry import cgm
from web.registry.cgm import base as cgm_base

# Dependencies
import web.core

# Load modules for all supported platforms
import web.core.cgm.openwrt
import web.core.cgm.ubnt

# Register CGM validator
@registration.register_validation_hook("node.config")
def node_cgm_validation(node):
  """
  Performs validation of node configuration via CGM.
  """
  try:
    cgm.generate_config(node, only_validate = True)
  except cgm_base.ValidationError, e:
    raise registry_forms.RegistryValidationError(*e.args)

