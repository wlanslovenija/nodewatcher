from nodewatcher.core.generator.cgm.defaults import NetworkModuleMixin
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms

from .base import ClearInterfaces, NetworkProfile


class MobileUplinkModule(NetworkModuleMixin, registry_forms.FormDefaultsModule):
    """
    Form defaults module for configuring mobile uplinks.
    """

    requires = [
        NetworkProfile(),
        ClearInterfaces()
    ]

    def pre_configure(self, context, state, create):
        mobile_defaults = None
        for mobile_interface in state.filter_items('core.interfaces', klass=cgm_models.MobileInterfaceConfig):
            mobile_defaults = mobile_interface
            break

        context['mobile_defaults'] = mobile_defaults

    def configure(self, context, state, create):
        network_profiles = context['network_profiles']
        mobile_defaults = context['mobile_defaults']

        if 'mobile-uplink' in network_profiles:
            if mobile_defaults is not None:
                # Reuse some configuration form the previous mobile interface.
                self.setup_interface(
                    state,
                    cgm_models.MobileInterfaceConfig,
                    configuration={
                        'service': mobile_defaults.service,
                        'device': mobile_defaults.device,
                        'apn': mobile_defaults.apn,
                        'pin': mobile_defaults.pin,
                        'username': mobile_defaults.username,
                        'password': mobile_defaults.password,
                        'uplink': True,
                    }
                )
            else:
                # Create a new mobile interface.
                self.setup_interface(
                    state,
                    cgm_models.MobileInterfaceConfig,
                    configuration={
                        'service': 'umts',
                        'device': 'ppp0',
                        'uplink': True,
                    }
                )
