from django import forms

from nodewatcher.core.allocation.ip import forms as ip_forms
from nodewatcher.core.registry import registration

from . import models

class BasicAddressingConfigForm(forms.ModelForm, ip_forms.IpAddressAllocatorFormMixin):
    """
    General configuration form.
    """

    class Meta:
        model = models.BasicAddressingConfig

registration.register_form_for_item(models.BasicAddressingConfig, BasicAddressingConfigForm)
