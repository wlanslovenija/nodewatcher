from django import forms
from django.db.models import fields
from django.utils.translation import ugettext as _

from . import models, base as cgm_base
from ...allocation.ip import forms as ip_forms
from ...registry import fields as registry_fields, registration

class WifiInterfaceConfigForm(forms.ModelForm):
    """
    Wifi interface configuration form.
    """
    class Meta:
        model = models.WifiInterfaceConfig

registration.register_form_for_item(models.WifiInterfaceConfig, WifiInterfaceConfigForm)

class AllocatedNetworkConfigForm(forms.ModelForm, ip_forms.IpAddressAllocatorFormMixin):
    """
    General configuration form.
    """
    class Meta:
        model = models.AllocatedNetworkConfig

registration.register_form_for_item(models.AllocatedNetworkConfig, AllocatedNetworkConfigForm)

class VpnNetworkConfigForm(forms.ModelForm):
    """
    VPN uplink configuration form.
    """
    port = forms.IntegerField(min_value = 1, max_value = 49151)

    class Meta:
        model = models.VpnNetworkConfig

registration.register_form_for_item(models.VpnNetworkConfig, VpnNetworkConfigForm)

class WifiRadioDeviceConfigForm(forms.ModelForm):
    """
    A wireless radio device configuration form.
    """
    class Meta:
        model = models.WifiRadioDeviceConfig

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
            radio = cgm_base.get_platform(cfg['core.general'][0].platform)\
            .get_router(cfg['core.general'][0].router)\
            .get_radio(item.wifi_radio)

            # Protocols
            self.fields['protocol'] = registry_fields.SelectorFormField(
                label = _("Protocol"),
                choices = fields.BLANK_CHOICE_DASH + list(radio.get_protocol_choices()),
                coerce = str,
                empty_value = None
            )

            # Antenna connectors
            self.fields['antenna_connector'] = registry_fields.SelectorFormField(
                label = _("Connector"),
                choices = [("", _("[auto-select]"))] + list(radio.get_connector_choices()),
                coerce = str,
                empty_value = None,
                required = False
            )
        except (KeyError, IndexError, AttributeError):
            # Create empty fields on error
            self.fields['protocol'] = registry_fields.SelectorFormField(label = _("Protocol"), choices = fields.BLANK_CHOICE_DASH)
            self.fields['channel'] = registry_fields.SelectorFormField(label = _("Channel"), choices = fields.BLANK_CHOICE_DASH)
            self.fields['antenna_connector'] = registry_fields.SelectorFormField(label = _("Connector"), choices = fields.BLANK_CHOICE_DASH)
            return

        # Channels
        try:
            self.fields['channel'] = registry_fields.SelectorFormField(
                label = _("Channel"),
                choices = fields.BLANK_CHOICE_DASH + list(radio.get_protocol(item.protocol).get_channel_choices(self.regulatory_filter(request))),
                coerce = str,
                empty_value = None
            )
        except (KeyError, AttributeError):
            # Create empty field on error
            self.fields['channel'] = registry_fields.SelectorFormField(label = _("Channel"), choices = fields.BLANK_CHOICE_DASH)

registration.register_form_for_item(models.WifiRadioDeviceConfig, WifiRadioDeviceConfigForm)
