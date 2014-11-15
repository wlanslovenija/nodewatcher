from django import forms

from nodewatcher.core.registry import registration

from . import models


class TunneldiggerServerConfigForm(forms.ModelForm):
    """
    Tunneldigger uplink configuration form.
    """

    port = forms.IntegerField(min_value=1, max_value=49151)

    class Meta:
        model = models.TunneldiggerServerConfig

registration.register_form_for_item(models.TunneldiggerServerConfig, TunneldiggerServerConfigForm)
