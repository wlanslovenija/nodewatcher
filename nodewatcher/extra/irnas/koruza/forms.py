from django import forms
from django.forms import fields as widgets
from django.utils import encoding
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.registry import registration

from . import models


class KoruzaPeerSelectionField(forms.ModelChoiceField):
    def __init__(self, **kwargs):
        # TODO: Limit only to nodes which have the KORUZA package installed.
        kwargs['queryset'] = core_models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
        ).order_by(
            # TODO: Nodes should be sorted by distance from current node.
            'name'
        )

        kwargs['widget'] = widgets.Select(attrs={'class': 'registry_form_selector'})

        super(KoruzaPeerSelectionField, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return encoding.smart_text(obj.name)


class KoruzaConfigForm(forms.ModelForm):
    """
    KORUZA controller unit configuration form.
    """

    class Meta:
        model = models.KoruzaConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Handles peer controller configuration
        """

        self.fields['peer_controller'] = KoruzaPeerSelectionField(
            empty_label=_("[none]"),
            label=_("Peer controller"),
            required=False,
        )

registration.register_form_for_item(models.KoruzaConfig, KoruzaConfigForm)
