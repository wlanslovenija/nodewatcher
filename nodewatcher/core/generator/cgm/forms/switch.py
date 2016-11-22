from django import forms
from django.db.models import fields
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import forms as registry_forms, registration

from .. import models


class SwitchConfigForm(forms.ModelForm):
    """
    Switch configuration form.
    """

    class Meta:
        model = models.SwitchConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically configures the switch configuration form.
        """

        try:
            device = cfg['core.general'][0].get_device()
            switch = device.get_switch(item.switch)

            self.fields['vlan_preset'] = registry_forms.RegistryChoiceFormField(
                label=_("VLAN Preset"),
                choices=list(switch.get_preset_choices()),
                empty_value='default'
            )
        except (KeyError, IndexError, AttributeError):
            self.fields['vlan_preset'] = registry_forms.RegistryChoiceFormField(
                label=_("VLAN Preset"),
                choices=[],
            )

registration.register_form_for_item(models.SwitchConfig, SwitchConfigForm)


class VLANConfigForm(forms.ModelForm):
    """
    Switch VLAN configuration form.
    """

    class Meta:
        model = models.VLANConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically configures the switch configuration form.
        """

        try:
            device = cfg['core.general'][0].get_device()
            switch = device.get_switch(item.switch.switch)

            # VLAN identifiers.
            self.fields['vlan'] = registry_forms.RegistryChoiceFormField(
                label=_("VLAN"),
                choices=fields.BLANK_CHOICE_DASH + list(switch.get_vlan_choices()),
                empty_value=None,
                coerce=int,
            )

            # Ports.
            self.fields['ports'] = registry_forms.RegistryMultipleChoiceFormField(
                label=_("Ports"),
                choices=list(switch.get_port_choices()),
                empty_value=None,
                coerce=int,
            )
        except (KeyError, IndexError, AttributeError):
            self.fields['vlan'] = registry_forms.RegistryChoiceFormField(
                label=_("VLAN"),
                choices=[],
                empty_value=None,
                coerce=int,
            )

            self.fields['ports'] = registry_forms.RegistryMultipleChoiceFormField(
                label=_("Ports"),
                choices=[],
                empty_value=None,
                coerce=int,
            )

registration.register_form_for_item(models.VLANConfig, VLANConfigForm)


class EthernetInterfaceConfigForm(forms.ModelForm):
    """
    Ethernet interface configuration form.
    """

    class Meta:
        model = models.EthernetInterfaceConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically configures the ethernet interface configuration form.
        """

        ethernet_ports = []

        # Include all device ports.
        try:
            device = cfg['core.general'][0].get_device()
            ethernet_ports.extend([(port.identifier, port.description) for port in device.ports])

            # Include all switch ports.
            for switch in cfg['core.switch']:
                switch_descriptor = device.get_switch(switch.switch)
                for vlan in switch.vlans:
                    ethernet_ports.append(
                        (switch_descriptor.get_port_identifier(vlan.vlan), unicode(vlan))
                    )
        except (KeyError, IndexError, AttributeError):
            pass

        self.fields['eth_port'] = registry_forms.RegistryChoiceFormField(
            label=_("Port"),
            choices=ethernet_ports,
        )

registration.register_form_for_item(models.EthernetInterfaceConfig, EthernetInterfaceConfigForm)


class DefaultSwitchConfiguration(registry_forms.FormDefaults):
    """
    Handles automatic switch configuration from device descriptor defaults.
    """

    # Switch defaults must always be applied for correct preset handling.
    always_apply = True

    def set_defaults(self, state, create):
        # Get device descriptor.
        general_config = state.lookup_item(models.CgmGeneralConfig)
        if not general_config or not hasattr(general_config, 'router') or not general_config.router:
            # Return if no device is selected.
            return

        device = general_config.get_device()
        if not device:
            return

        for switch in device.switches:
            switch_config = state.filter_items('core.switch', klass=models.SwitchConfig, switch=switch.identifier)
            # TODO: Trigger a validation error if there are multiple switch configs for the same switch.

            # If a specific switch does not exist, create it.
            if not switch_config:
                switch_config = state.append_item(
                    models.SwitchConfig,
                    switch=switch.identifier,
                    vlan_preset='default'
                )
            else:
                switch_config = switch_config[0]

            # Generate configuration for the given preset.
            preset = switch.get_preset(switch_config.vlan_preset)
            if not preset.custom:
                # If the preset does not allow custom configurations, remove all existing configurations.
                state.remove_items('core.switch.vlan', parent=switch_config)

            for vlan in preset.vlans:
                # Remove any configurations for the same VLAN.
                state.remove_items('core.switch.vlan', parent=switch_config, vlan=vlan.vlan)

                # Create configuration for this VLAN.
                state.append_item(
                    models.VLANConfig,
                    parent=switch_config,
                    name=vlan.description,
                    vlan=vlan.vlan,
                    ports=vlan.ports
                )

        # Remove all switches, which are defined but do not exist on the target device.
        for switch_config in state.filter_items('core.switch', klass=models.SwitchConfig):
            if not device.get_switch(switch_config.switch):
                state.remove_items('core.switch', switch=switch_config.switch)

registration.point('node.config').add_form_defaults(DefaultSwitchConfiguration())
