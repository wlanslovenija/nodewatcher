from django import forms

from nodewatcher.core.registry import registration

from . import models


class OlsrdModTxtinfoPackageConfigForm(forms.ModelForm):
    """
    Configuration form for olsrd-mod-txtinfo package.
    """

    port = forms.IntegerField(min_value=1, max_value=49151)

    class Meta:
        model = models.OlsrdModTxtinfoPackageConfig

registration.register_form_for_item(models.OlsrdModTxtinfoPackageConfig, OlsrdModTxtinfoPackageConfigForm)
