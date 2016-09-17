from django import forms
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration

from .. import models


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
            qs = qs.filter(builders__channels=item.build_channel).distinct()
        else:
            qs = qs.none()
        self.fields['version'].queryset = qs

registration.register_form_for_item(models.CgmGeneralConfig, CgmGeneralConfigForm)
