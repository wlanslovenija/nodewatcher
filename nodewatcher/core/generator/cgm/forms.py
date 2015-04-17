from django import forms
from django.db.models import fields
from django.forms import fields as widgets
from django.utils import encoding
from django.utils.translation import ugettext as _

from ... import models as core_models
from ...allocation.ip import forms as ip_forms
from ...registry import forms as registry_forms, registration

from . import models, base as cgm_base


class CgmGeneralConfigForm(forms.ModelForm):
    """
    General CGM configuration form.
    """

    class Meta:
        model = models.CgmGeneralConfig
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(CgmGeneralConfigForm, self).__init__(*args, **kwargs)
        self.fields['build_channel'].empty_label = _('(default)')
        self.fields['build_channel'].widget.choices = self.fields['build_channel'].choices
        self.fields['version'].empty_label = _('(latest)')
        self.fields['version'].widget.choices = self.fields['version'].choices

    def modify_to_context(self, item, cfg, request):
        """
        Handles dynamic version selection.
        """

        qs = self.fields['version'].queryset
        if item is not None:
            qs = qs.filter(builders__channels=item.build_channel)
        else:
            qs = qs.none()
        self.fields['version'].queryset = qs

registration.register_form_for_item(models.CgmGeneralConfig, CgmGeneralConfigForm)


class AccessPointSelectionField(forms.ModelChoiceField):
    def __init__(self, protocol, **kwargs):
        kwargs['queryset'] = core_models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
            wifi_interface='core.interfaces',
            wifi_mode='core.interfaces#mode',
        ).filter(
            # Only show nodes which have access point interfaces configured.
            wifi_mode='ap',
            # Only show access point interfaces that are of the same mode as the station.
            wifi_interface__device__protocol=protocol,
        ).order_by(
            # TODO: Nodes should be sorted by distance from current node.
            'name'
        )

        kwargs['widget'] = widgets.Select(attrs={'class': 'registry_form_selector'})

        super(AccessPointSelectionField, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return encoding.smart_text(obj.name)


class WifiInterfaceConfigForm(forms.ModelForm):
    """
    Wifi interface configuration form.
    """

    class Meta:
        model = models.WifiInterfaceConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Handles "connect to existing AP" functionality for STA VIFs.
        """

        if item.mode == 'sta':
            self.fields['connect_to'] = AccessPointSelectionField(
                protocol=item.device.protocol,
                empty_label=_("[manually configured AP]"),
                label=_("Connect to existing AP"),
                required=False,
            )

            # If any node is actually selected, we should hide manual configuration options.
            if item.connect_to is not None:
                del self.fields['essid']
                del self.fields['bssid']
        else:
            # If mode is not set to STA, hide the connect to field.
            del self.fields['connect_to']

registration.register_form_for_item(models.WifiInterfaceConfig, WifiInterfaceConfigForm)


class AllocatedNetworkConfigForm(forms.ModelForm, ip_forms.IpAddressAllocatorFormMixin):
    """
    General configuration form.
    """

    class Meta:
        model = models.AllocatedNetworkConfig
        fields = '__all__'

registration.register_form_for_item(models.AllocatedNetworkConfig, AllocatedNetworkConfigForm)


class WifiRadioDeviceConfigForm(forms.ModelForm):
    """
    A wireless radio device configuration form.
    """

    tx_power = widgets.IntegerField(min_value=1, max_value=27, required=False)

    class Meta:
        model = models.WifiRadioDeviceConfig
        fields = '__all__'

    def regulatory_filter(self, request):
        """
        Subclasses may override this method to filter the channels accoording to a
        filter for a regulatory domain. It should return a list of frequencies that
        are allowed.
        """

        return None

    def modify_to_context(self, item, cfg, request):
        """
        Handles dynamic protocol/channel selection.
        """

        radio = None
        try:
            radio = cgm_base.get_platform(
                cfg['core.general'][0].platform
            ).get_device(
                cfg['core.general'][0].router
            ).get_radio(
                item.wifi_radio
            )

            # Protocols
            self.fields['protocol'] = registry_forms.RegistryChoiceFormField(
                label=_("Protocol"),
                choices=fields.BLANK_CHOICE_DASH + list(radio.get_protocol_choices()),
                coerce=str,
                empty_value=None,
            )

            # Antenna connectors
            self.fields['antenna_connector'] = registry_forms.RegistryChoiceFormField(
                label=_("Connector"),
                choices=[("", _("[auto-select]"))] + list(radio.get_connector_choices()),
                coerce=str,
                empty_value=None,
                required=False,
            )
        except (KeyError, IndexError, AttributeError):
            # Create empty fields on error
            self.fields['protocol'] = registry_forms.RegistryChoiceFormField(label=_("Protocol"), choices=fields.BLANK_CHOICE_DASH)
            self.fields['channel'] = registry_forms.RegistryChoiceFormField(label=_("Channel"), choices=fields.BLANK_CHOICE_DASH, required=True)
            self.fields['antenna_connector'] = registry_forms.RegistryChoiceFormField(label=_("Connector"), choices=fields.BLANK_CHOICE_DASH)
            return

        # Channel widths
        try:
            self.fields['channel_width'] = registry_forms.RegistryChoiceFormField(
                label=_("Channel Width"),
                choices=fields.BLANK_CHOICE_DASH + list(
                    radio.get_protocol(item.protocol).get_channel_width_choices()
                ),
                coerce=str,
                empty_value=None,
            )
        except (KeyError, AttributeError):
            # Create empty field on error
            self.fields['channel_width'] = registry_forms.RegistryChoiceFormField(label=_("Channel Width"), choices=fields.BLANK_CHOICE_DASH)

        # Channels
        try:
            channel_width = radio.get_protocol(item.protocol).get_channel_width(item.channel_width)
            self.fields['channel'] = registry_forms.RegistryChoiceFormField(
                label=_("Channel"),
                choices=[("", _("[auto-select]"))] + list(
                    radio.get_protocol(item.protocol).get_channel_choices(channel_width, self.regulatory_filter(request))
                ),
                coerce=str,
                empty_value=None,
                required=False,
            )
        except (KeyError, AttributeError):
            # Create empty field on error
            self.fields['channel'] = registry_forms.RegistryChoiceFormField(label=_("Channel"), choices=fields.BLANK_CHOICE_DASH, required=True)

registration.register_form_for_item(models.WifiRadioDeviceConfig, WifiRadioDeviceConfigForm)
