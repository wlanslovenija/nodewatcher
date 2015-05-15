from django import forms

from nodewatcher.core.registry import registration

from . import models, widgets


class PublicKeyIdentityConfigForm(forms.ModelForm):
    """
    Location configuration form.
    """

    class Meta:
        model = models.PublicKeyIdentityConfig
        fields = '__all__'
        widgets = {
            'public_key': widgets.PublicKeyWidget()
        }

registration.register_form_for_item(models.PublicKeyIdentityConfig, PublicKeyIdentityConfigForm)
