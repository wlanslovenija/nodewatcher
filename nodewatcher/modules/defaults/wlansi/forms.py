from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms, registration


class STAChannelAutoselect(registry_forms.FormDefaults):
    """
    Configures any radios containing VIFs in STA mode to have automatic
    channel selection.
    """

    def set_defaults(self, state):
        # Iterate over all configured radios and VIFs.
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            # TODO: Improve this filtering.
            for vif in state.filter_items('core.interfaces', klass=cgm_models.WifiInterfaceConfig, parent=radio):
                if vif.mode != 'sta':
                    continue

                # Ensure that the parent radio has the channel set to auto.
                state.update_item(vif.device, channel=None)

registration.point('node.config').add_form_defaults(STAChannelAutoselect())
