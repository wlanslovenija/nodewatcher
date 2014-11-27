from django import forms

from nodewatcher.core.registry import registration

from . import models


class PublicKeyAuthenticationConfigForm(forms.ModelForm):
    """
    Public key authentication config form.
    """

    class Meta:
        model = models.PublicKeyAuthenticationConfig

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """

        # Only allow selection of user's public keys
        qs = self.fields['public_key'].queryset
        qs = qs.filter(user=request.user)
        self.fields['public_key'].queryset = qs

registration.register_form_for_item(models.PublicKeyAuthenticationConfig, PublicKeyAuthenticationConfigForm)
