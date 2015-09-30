import re

from django.db import models
from django.db.models import fields
from django.forms import fields as form_fields, widgets
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'RegistryChoiceFormField', 'RegistryMultipleChoiceFormField',
    'MACAddressFormField', 'IPAddressFormField',
    'ReferenceChoiceFormField'
)


class RegistryChoiceFormFieldMixin(object):

    accepts_multiple_choices = False

    def modify_to_context(self, item, cfg, request):
        """
        Adapts the field to current registry context.
        """

        if self._rp_choices is None:
            return

        def resolve_registry_id(loc):
            registry_id, attribute = loc.split('#')
            try:
                return reduce(getattr, attribute.split('.'), cfg[registry_id][0])
            except (KeyError, IndexError, AttributeError):
                return None

        prepend_choices = []
        if not self.accepts_multiple_choices:
            prepend_choices = fields.BLANK_CHOICE_DASH
        self.choices = prepend_choices + self._rp_choices.subset_choices(lambda registry_id, value: resolve_registry_id(registry_id) == value)


class RegistryChoiceFormField(form_fields.TypedChoiceField, RegistryChoiceFormFieldMixin):
    """
    An augmented TypedChoiceField that gets updated by client-side AJAX on every
    change and can handle dependent choices.
    """

    def __init__(self, rp_choices=None, *args, **kwargs):
        """
        Class constructor.
        """

        kwargs['widget'] = widgets.Select(attrs={'class': 'registry_form_selector'})
        super(RegistryChoiceFormField, self).__init__(*args, **kwargs)

        # Override choices so we get a lazy list instead of being evaluated right here.
        self._rp_choices = None
        if rp_choices is not None:
            self._rp_choices = self._choices = self.widget.choices = rp_choices


class RegistryMultipleChoiceFormField(form_fields.TypedMultipleChoiceField, RegistryChoiceFormFieldMixin):
    """
    An augmented TypedMultipleChoiceField that gets updated by client-side AJAX on every
    change and can handle dependent choices.
    """

    accepts_multiple_choices = True

    def __init__(self, rp_choices=None, *args, **kwargs):
        """
        Class constructor.
        """

        kwargs['widget'] = widgets.CheckboxSelectMultiple(attrs={'class': 'registry_form_selector'})
        super(RegistryMultipleChoiceFormField, self).__init__(*args, **kwargs)

        # Override choices so we get a lazy list instead of being evaluated right here.
        self._rp_choices = None
        if rp_choices is not None:
            self._rp_choices = self._choices = self.widget.choices = rp_choices

MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)


class MACAddressFormField(form_fields.RegexField):
    """
    Form field for MAC/BSSID addresses.
    """

    default_error_messages = {
        'invalid': _("Enter a valid MAC address."),
    }

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(MACAddressFormField, self).__init__(mac_re, *args, **kwargs)


class IPAddressFormField(form_fields.CharField):
    """
    IP address form field.
    """

    def prepare_value(self, value):
        """
        Prepare field value for display inside the form.
        """

        if value is None:
            return None

        value = str(value)
        if value.endswith('/32'):
            value = value[:-3]
        return value


class ReferenceChoiceFormField(form_fields.TypedChoiceField):
    """
    Form field for :class:`ReferenceChoiceField` database field.
    """

    def __init__(self, choices_model, *args, **kwargs):
        """
        Class constructor.

        :param choices_model: Choices model class
        """

        self.choices_rid = choices_model._registry.registry_id
        self.filter_model = choices_model
        self.partially_validated_tree = None
        self.limit_choices_to = kwargs.pop('limit_choices_to', None) or (lambda model: True)
        kwargs['widget'] = widgets.Select(attrs={'class': 'registry_form_selector'})
        kwargs['empty_value'] = None
        super(ReferenceChoiceFormField, self).__init__(*args, **kwargs)

    def get_dependencies(self, value):
        """
        Returns a list of dependencies on other registry forms. This method will
        only be called when form validation succeeds and the form is scheduled
        to be saved.

        :param value: Cleaned value
        :return: A list of dependency tuples (cfg_location, id(cfg_parent), cfg_index)
        """

        if value is None:
            return []

        return [(self.choices_rid, id(None), value)]

    def modify_to_context(self, item, cfg, request):
        """
        Limits the valid choices to items from the partially validated configuration.
        """

        self.choices = []

        if not self.required:
            self.choices += fields.BLANK_CHOICE_DASH

        self.choices += [
            (index, model)
            for index, model in enumerate(cfg.get(self.choices_rid, []))
            if isinstance(model, self.filter_model) and self.limit_choices_to(model)
        ]

        # Store the partially validated tree on which the choices are based
        self.partially_validated_tree = cfg

    def prepare_value(self, value):
        if isinstance(value, self.filter_model):
            for index, model in self.choices:
                if index == '':
                    continue

                if value.pk == model.pk or value.pk == getattr(model, '_original_pk', ''):
                    return index

        return super(ReferenceChoiceFormField, self).prepare_value(value)

    def to_python(self, value):
        if value is None or not self.partially_validated_tree:
            return None

        try:
            model = self.partially_validated_tree[self.choices_rid][int(value)]
            if not model.pk:
                return None

            return model
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def valid_value(self, value):
        if value is None:
            return True

        for index, model in self.choices:
            if index == '':
                continue

            if isinstance(model, models.Model):
                try:
                    if value == self.partially_validated_tree[self.choices_rid][index]:
                        return True
                except (KeyError, IndexError):
                    pass
            else:
                try:
                    if int(value) == index:
                        return True
                except ValueError:
                    pass

        return False
