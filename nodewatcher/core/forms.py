from django import forms

from . import models
from .allocation.ip import forms as ip_forms
from .registry import registration

class BasicAddressingConfigForm(forms.ModelForm, ip_forms.IpAddressAllocatorFormMixin):
    """
    General configuration form.
    """

    class Meta:
        model = models.BasicAddressingConfig

registration.register_form_for_item(models.BasicAddressingConfig, BasicAddressingConfigForm)
