from nodewatcher.core.registry import forms as registry_forms

from . import models


class Name(registry_forms.FormDefaultsModule):
    """
    Form defaults module that stores node's name into the module
    context. If no general node configuration is available, defaults
    processing of the parent module is aborted.

    Exported context properties:
    - ``name`` contains the node name
    """

    def pre_configure(self, context, state, create):
        """
        Get node name for the node in question.
        """

        general_config = state.lookup_item(models.GeneralConfig)
        if not general_config:
            # Abort configuration if no device is selected.
            raise registry_forms.StopDefaults

        context.update({
            'name': general_config.name,
        })
