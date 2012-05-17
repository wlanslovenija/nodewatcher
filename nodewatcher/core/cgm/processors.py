from nodewatcher.registry import registration
from nodewatcher.registry import forms as registry_forms
from nodewatcher.registry import cgm
from nodewatcher.registry.cgm import base as cgm_base
from nodewatcher.registry.forms import processors

# Dependencies
import nodewatcher.core

# Load modules for all supported platforms
import nodewatcher.core.cgm.openwrt
import nodewatcher.core.cgm.ubnt

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
