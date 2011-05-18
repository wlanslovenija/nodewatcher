from registry import registration
from registry import forms as registry_forms
from registry import cgm
from registry.cgm import base as cgm_base

# Dependencies
import core

# Load modules for all supported platforms
import core.cgm.openwrt
import core.cgm.ubnt

# Register CGM validator
@registration.register_validation_hook("node.config")
def node_cgm_validation(node):
  """
  Performs validation of node configuration via CGM.
  """
  try:
    cgm.generate_config(node, only_validate = True)
  except cgm_base.ValidationError, e:
    raise registry_forms.RegistryValidationError(e.args[0])

