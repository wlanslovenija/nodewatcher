from django import forms

from nodewatcher.core.registry import registration

from . import uplink
from .. import models


class BridgeInterfaceConfigForm(uplink.UplinkableFormMixin, forms.ModelForm):
    class Meta:
        model = models.BridgeInterfaceConfig
        fields = '__all__'

registration.register_form_for_item(models.BridgeInterfaceConfig, BridgeInterfaceConfigForm)
