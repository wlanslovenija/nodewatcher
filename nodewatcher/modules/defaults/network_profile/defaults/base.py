from nodewatcher.core.registry import forms as registry_forms

from nodewatcher.modules.vpn.tunneldigger import models as td_models

from .. import models


class NetworkProfile(registry_forms.FormDefaultsModule):
    """
    Form defaults module that stores node's network profiles into the
    module context.

    Exported context properties:
    - ``network_profiles`` contains a list of network profile strings
    """

    def pre_configure(self, context, state, create):
        """
        Get node type for the node that is being edited.
        """

        network_profile_config = state.lookup_item(models.NetworkProfileConfig)
        if not network_profile_config or not network_profile_config.profiles:
            network_profiles = []
        else:
            network_profiles = network_profile_config.profiles

        context['network_profiles'] = network_profiles


class ClearInterfaces(registry_forms.FormDefaultsModule):
    """
    Form defaults module that removes all interfaces during the configuration
    stage.
    """

    def configure(self, context, state, create):
        def filter_remove_item(item):
            # Do not remove tunneldigger interfaces as they are already handled by other
            # defaults handlers.
            if isinstance(item, td_models.TunneldiggerInterfaceConfig):
                return False

            # Remove everything else.
            return True
        state.remove_items('core.interfaces', filter=filter_remove_item)
