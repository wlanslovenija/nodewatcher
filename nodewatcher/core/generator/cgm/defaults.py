from django.utils import crypto

from nodewatcher.core.registry import forms as registry_forms

from . import models


class DefaultPlatform(registry_forms.FormDefaults):
    """
    Default platform configuration.
    """

    def __init__(self, platform):
        self.platform = platform

    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default platform.
        general_config = state.lookup_item(models.CgmGeneralConfig)
        if not general_config:
            state.append_item(models.CgmGeneralConfig, platform=self.platform)
        elif not general_config.platform:
            state.update_item(general_config, platform=self.platform)


class DefaultRandomPassword(registry_forms.FormDefaults):
    """
    Default random password.
    """

    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Generate a default random password in case no authentication is configured.
        try:
            state.filter_items('core.authentication')[0]
        except IndexError:
            state.append_item(
                models.PasswordAuthenticationConfig,
                password=crypto.get_random_string(),
            )


class STAChannelAutoselect(registry_forms.FormDefaults):
    """
    Configures any radios containing VIFs in STA mode to have automatic
    channel selection.
    """

    def set_defaults(self, state, create):
        # Iterate over all configured radios and VIFs.
        for radio in state.filter_items('core.interfaces', klass=models.WifiRadioDeviceConfig):
            all_vifs_sta = None
            for vif in state.filter_items('core.interfaces', klass=models.WifiInterfaceConfig, parent=radio):
                if all_vifs_sta is None and vif.mode == 'sta':
                    all_vifs_sta = True
                elif vif.mode != 'sta':
                    all_vifs_sta = False

            if all_vifs_sta:
                # Ensure that the parent radio has the channel set to auto.
                state.update_item(radio, channel='')


class Device(registry_forms.FormDefaultsModule):
    """
    Form defaults module that stores node's device descriptor into the
    module context. If no device is configured, defaults processing of
    the parent module is aborted.

    Exported context properties:
    - ``device`` contains the device descriptor
    """

    def pre_configure(self, context, state, create):
        """
        Get device descriptor for the node in question.
        """

        general_config = state.lookup_item(models.CgmGeneralConfig)
        if not general_config or not hasattr(general_config, 'router') or not general_config.router:
            # Abort configuration if no device is selected.
            raise registry_forms.StopDefaults

        device = general_config.get_device()
        if not device:
            raise registry_forms.StopDefaults

        context.update({
            'device': device,
        })


class NetworkModuleMixin(object):
    """
    Mixin for form defaults module with useful network-related methods.
    """

    def setup_item(self, state, registry_id, klass, configuration=None, annotations=None, **filter):
        # Create a new item.
        if configuration is None:
            configuration = {}

        filter.update(configuration)
        return state.append_item(klass, annotations=annotations, **filter)

    def setup_interface(self, state, klass, configuration=None, annotations=None, **filter):
        return self.setup_item(state, 'core.interfaces', klass, configuration, annotations, **filter)

    def setup_network(self, state, interface, klass, configuration=None, annotations=None, **filter):
        return self.setup_item(state, 'core.interfaces.network', klass, configuration, annotations, parent=interface, **filter)
