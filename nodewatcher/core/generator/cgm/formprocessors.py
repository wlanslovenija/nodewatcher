from ...registry import forms as registry_forms
from ...registry.forms import formprocessors

from . import base as cgm_base, exceptions


class NodeCgmValidator(formprocessors.RegistryFormProcessor):
    """
    A form processor that validates a node's firmware configuration via the
    Configuration Generating Modules (CGMs) ensuring that the configuration
    can be realized on an actual node.
    """

    def postprocess(self, node):
        """
        Validates node's firmware configuration.

        :param node: Node to validate the configuration for
        """

        try:
            cgm_base.generate_firmware(node, only_validate=True)
        except exceptions.BuilderConfigurationError:
            # Ignore builder configuration errors at this point as we are only trying
            # to validate configuration, not actually generating anything
            pass
        except cgm_base.ValidationError, e:
            raise registry_forms.RegistryValidationError(*e.args)
