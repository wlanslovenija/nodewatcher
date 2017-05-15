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
