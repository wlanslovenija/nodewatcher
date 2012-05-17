from frontend.registry import registration
from frontend.registry import forms as registry_forms
from frontend.registry import cgm
from frontend.registry.cgm import base as cgm_base
from frontend.registry.forms import processors

# Dependencies
import frontend.core

# Load modules for all supported platforms
import frontend.core.cgm.openwrt
import frontend.core.cgm.ubnt

class NodeCgmValidator(processors.RegistryFormProcessor):
  """
  A form processor that validates a node's firmware configuration via the
  Configuration Generating Modules (CGMs) ensuring that the configuration
  can be realized on an actual node.
  """
  def postprocess(self, node):
    """
    Validates node's firmware configuration.

    :param node: node to validate the configuration for
    """
    try:
      cgm.generate_config(node, only_validate = True)
    except cgm_base.ValidationError, e:
      raise registry_forms.RegistryValidationError(*e.args)
