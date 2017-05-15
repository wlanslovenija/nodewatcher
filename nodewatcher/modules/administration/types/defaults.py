from nodewatcher.core.registry import forms as registry_forms

from . import models


class DefaultType(registry_forms.FormDefaults):
    """
    Default node type configuration.
    """

    def __init__(self, type):
        self.type = type

    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default type.
        type_config = state.lookup_item(models.TypeConfig)
        if not type_config:
            state.append_item(models.TypeConfig, type=self.type)
        elif not type_config.type:
            state.update_item(type_config, type=self.type)
