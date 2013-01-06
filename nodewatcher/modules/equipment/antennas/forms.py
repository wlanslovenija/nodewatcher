from django import forms
from django.db import models
from django.forms import models as model_forms
from django.utils import datastructures
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration
from . import models as antenna_models

ANTENNA_FORM_FIELD_PREFIX = 'antenna_'

class AntennaEquipmentConfigFormMeta(model_forms.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        # Prepare fields for our model
        fields = datastructures.SortedDict()
        for fname, field in model_forms.fields_for_model(antenna_models.Antenna).items():
            fields['%s%s' % (ANTENNA_FORM_FIELD_PREFIX, fname)] = field
        attrs['_antenna_fields'] = fields
        return model_forms.ModelFormMetaclass.__new__(cls, name, bases, attrs)

class AntennaEquipmentConfigForm(forms.ModelForm):
    """
    Antenna equipment configuration form.
    """

    class Meta:
        model = antenna_models.AntennaEquipmentConfig

    __metaclass__ = AntennaEquipmentConfigFormMeta

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically displays fields for entering new antenna information.
        """

        self.fields['antenna'].empty_label = _("[Add new antenna]")
        try:
            qs = self.fields['antenna'].queryset
            qs = qs.filter(models.Q(internal_for = cfg['core.general'][0].router) | models.Q(internal_for = None))
            qs = qs.order_by("internal_for", "internal_id", "name")
            self.fields['antenna'].queryset = qs
        except (IndexError, KeyError, AttributeError):
            pass

        try:
            if item.antenna is not None:
                self._creating_antenna = False
                return
        except antenna_models.Antenna.DoesNotExist:
            pass

        # Generate fields for entering a new antenna
        self.fields.update(self._antenna_fields)
        self._creating_antenna = True
        self.fields['antenna'].required = False

    def save(self):
        """
        Creates a new antenna descriptor instance and saves it into the model.
        """

        if self._creating_antenna:
            # Prepare just the prefixed fields
            orig_cleaned_data = self.cleaned_data
            self.cleaned_data = {}
            for key, value in orig_cleaned_data.items():
                if key.startswith(ANTENNA_FORM_FIELD_PREFIX):
                    self.cleaned_data[key[len(ANTENNA_FORM_FIELD_PREFIX):]] = value

            # Create and save the new antenna instance
            antenna = antenna_models.Antenna()
            model_forms.save_instance(self, antenna, fail_message = 'created')
            self.cleaned_data = orig_cleaned_data
            self.instance.antenna = antenna

        return super(AntennaEquipmentConfigForm, self).save()

registration.register_form_for_item(antenna_models.AntennaEquipmentConfig, AntennaEquipmentConfigForm)
