from django import forms
from django.db import models as django_models

from nodewatcher.core.registry import registration

from . import models


class PublicKeyAuthenticationConfigForm(forms.ModelForm):
    """
    Public key authentication config form.
    """

    class Meta:
        model = models.PublicKeyAuthenticationConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """

        # Only allow selection of user's public keys. Also, if there are any existing
        # public keys set from other users, we should also allow those.
        qs = self.fields['public_key'].queryset
        query = django_models.Q(user=request.user)
        try:
            if item.public_key.pk:
                query |= django_models.Q(pk=item.public_key.pk)
        except (models.UserAuthenticationKey.DoesNotExist, AttributeError):
            pass

        qs = qs.filter(query)
        self.fields['public_key'].queryset = qs

registration.register_form_for_item(models.PublicKeyAuthenticationConfig, PublicKeyAuthenticationConfigForm)
