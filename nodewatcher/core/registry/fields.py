import os
import re

from django.core import exceptions
from django.db import models
from django.db.models import fields
from django.db.models.fields import related as related_fields
from django.forms import fields as form_fields, widgets
from django.utils import text
from django.utils.translation import ugettext_lazy as _

import south.modelsinspector

from ...utils import ipaddr

from . import registration, models as registry_models


class SelectorFormField(form_fields.TypedChoiceField):
    """
    An augmented TypedChoiceField that gets updated by client-side AJAX on every
    change and can handle dependent choices.
    """

    def __init__(self, rp_choices=None, *args, **kwargs):
        """
        Class constructor.
        """

        kwargs['widget'] = widgets.Select(attrs={'class': 'registry_form_selector'})
        super(SelectorFormField, self).__init__(*args, **kwargs)

        # Override choices so we get a lazy list instead of being evaluated right here
        self._rp_choices = None
        if rp_choices is not None:
            self._rp_choices = self._choices = self.widget.choices = rp_choices

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

        self.choices = fields.BLANK_CHOICE_DASH + self._rp_choices.subset_choices(lambda registry_id, value: resolve_registry_id(registry_id) == value)


class SelectorKeyField(models.CharField):
    """
    A character field that supports choices derived from a pre-registered choice set.
    When the field is rendered inside the registry formset, any modifications to it
    will cause the forms to be recomputed.
    """

    def __init__(self, regpoint, enum_id, *args, **kwargs):
        """
        Class constructor.
        """

        self.regpoint = regpoint
        self.enum_id = enum_id
        kwargs['max_length'] = 50
        self._rp_choices = kwargs['choices'] = registration.point(regpoint).get_registered_choices(enum_id).field_tuples()
        super(SelectorKeyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Returns an augmented form field.
        """

        defaults = {
            'required': not self.blank,
            'label': text.capfirst(self.verbose_name),
            'help_text': self.help_text,
            'rp_choices': self._rp_choices,
        }

        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        include_blank = self.blank or not (self.has_default() or 'initial' in kwargs)
        defaults['choices'] = self._rp_choices
        defaults['coerce'] = self.to_python
        if self.null:
            defaults['empty_value'] = None

        defaults.update(kwargs)
        return SelectorFormField(**defaults)


class ModelSelectorKeyField(models.ForeignKey):
    """
    A standard foreign key that augments the resulting form widget with a special
    selector class that will cause the forms to be recomputed when this field is
    modified.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        kwargs['on_delete'] = models.PROTECT
        super(ModelSelectorKeyField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Returns an augmented form field.
        """

        defaults = {'widget': widgets.Select(attrs={'class': 'registry_form_selector'})}
        defaults.update(kwargs)
        return super(ModelSelectorKeyField, self).formfield(**defaults)


class IntraRegistryRelatedObjectDescriptor(models.fields.related.ForeignRelatedObjectsDescriptor):
    """
    Descriptor for accessing related objects of a intra-registry foreign key that
    adds support for virtual relations in case of partially validated models.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(IntraRegistryRelatedObjectDescriptor, self).__init__(*args, **kwargs)

    def __get__(self, instance, instance_type=None):
        """
        Adds support for accessing virtual relations, since partially validated models
        can't be saved and therefore references don't work.
        """

        if not hasattr(instance, '_registry_virtual_model'):
            return super(IntraRegistryRelatedObjectDescriptor, self).__get__(instance, instance_type)
        elif instance is None:
            return self
        else:
            return getattr(instance, '_registry_virtual_relation', {}).get(self, [])

    def __set__(self, instance, value):
        """
        Adds support for setting virtual relations, since partially validated models
        can't be saved and therefore references don't work.
        """

        if not hasattr(instance, '_registry_virtual_model'):
            super(IntraRegistryRelatedObjectDescriptor, self).__set__(instance, value)
        else:
            instance._registry_virtual_relation[self] = value


class IntraRegistryForeignKey(models.ForeignKey):
    """
    A field for connecting registry items into a hierarchy.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(IntraRegistryForeignKey, self).__init__(*args, **kwargs)

    def contribute_to_related_class(self, cls, related):
        """
        Modifies the accessor descriptor so our own class is used instead of
        the standard one.
        """

        super(IntraRegistryForeignKey, self).contribute_to_related_class(cls, related)
        setattr(cls, related.get_accessor_name(), IntraRegistryRelatedObjectDescriptor(related))

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


class MACAddressField(models.Field):
    """
    Model field for MAC/BSSID addresses.
    """

    empty_strings_allowed = False

    def __init__(self, auto_add=False, *args, **kwargs):
        """
        Class constructor.
        """

        self.auto_add = auto_add
        if auto_add:
            kwargs['editable'] = False

        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Automatically generate a virtual MAC address when requested.
        """

        if self.auto_add and add:
            value = '00:ff:%02x:%02x:%02x:%02x' % tuple([ord(x) for x in os.urandom(4)])
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(MACAddressField, self).pre_save(model_instance, add)

    def get_internal_type(self):
        """
        Returns the underlying field type.
        """

        return 'CharField'

    def formfield(self, **kwargs):
        """
        Returns a MACAddressFormField instance for this model field.
        """

        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)


class IPAddressField(models.Field):
    """
    An IP address field that is backed by PostgreSQL inet type and uses ipaddr-py for
    Python address representation. It can store an address with an optional subnet
    netmask in CIDR notation.
    """

    __metaclass__ = models.SubfieldBase

    default_error_messages = {
        'invalid': _("Enter a valid IP address in CIDR notation."),
        'subnet_required': _("Enter a valid IP address with subnet in CIDR notation."),
        'host_required': _("Enter a valid host IP address."),
    }

    def __init__(self, subnet_required=False, host_required=False, *args, **kwargs):
        """
        Class constructor.

        :param subnet_required: Set to True when a subnet must be entered
        :param host_required: Set to True when a host must be entered
        """

        if subnet_required and host_required:
            raise ValueError("subnet_required and host_required options are mutually exclusive!")

        self.subnet_required = subnet_required
        self.host_required = host_required
        super(IPAddressField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        """
        Returns the database column type.
        """

        # XXX This extra space is there so that stupid Django PostgreSQL backend
        #     doesn't mangle the column by casting it via HOST() in WHERE clauses. A
        #     cleaner approach would be to override the WhereNode and fix make_atom,
        #     then integrate this with our augmented QuerySet.
        return 'inet '

    @staticmethod
    def ip_to_python(value, error_messages):
        if not value:
            return None

        if isinstance(value, ipaddr._IPAddrBase):
            return value

        try:
            return ipaddr.IPNetwork(value.encode('latin-1'))
        except ValueError:
            raise exceptions.ValidationError(error_messages['invalid'])

    def to_python(self, value):
        """
        Converts a database value into a Python one.
        """

        return self.ip_to_python(value, self.error_messages)

    def validate(self, value, model_instance):
        """
        Performs field validation.
        """

        super(IPAddressField, self).validate(value, model_instance)

        # Validate subnet size
        if self.subnet_required and value.numhosts <= 1:
            raise exceptions.ValidationError(self.error_messages['subnet_required'])
        elif self.host_required and value.numhosts > 1:
            raise exceptions.ValidationError(self.error_messages['host_required'])

    def get_prep_value(self, value):
        """
        Prepares Python value for saving into the database.
        """

        if not value:
            return None
        if isinstance(value, ipaddr._IPAddrBase):
            value = str(value)

        return unicode(value)

    def formfield(self, **kwargs):
        """
        Returns a proper form field instance.
        """

        defaults = {'form_class': IPAddressFormField}
        defaults.update(kwargs)
        return super(IPAddressField, self).formfield(**defaults)


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

    def to_python(self, value):
        """
        Performs IP address validation.
        """

        return IPAddressField.ip_to_python(value, IPAddressField.default_error_messages)


class ReferenceChoiceField(models.ForeignKey):
    """
    Foreign key that can be used to reference registry items from other
    subforms for the same node.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        kwargs['null'] = True
        kwargs['blank'] = True
        super(ReferenceChoiceField, self).__init__(*args, **kwargs)

    def _validate_relation(self, field, model, cls):
        """
        Performs relation validation after the destination model is fully resolved.
        """

        if not issubclass(cls, registry_models.RegistryItemBase):
            raise exceptions.ImproperlyConfigured(
                'ReferenceChoiceField can only be used in registry item models!'
            )

        if not issubclass(self.rel.to, registry_models.RegistryItemBase):
            raise exceptions.ImproperlyConfigured(
                'ReferenceChoiceField requires a relation with a registry item!'
            )

        if cls.get_registry_regpoint() != self.rel.to.get_registry_regpoint():
            raise exceptions.ImproperlyConfigured(
                'ReferenceChoiceField can only reference items registered under the same registration point!'
            )

    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        Ensure that field validation is run after the destination model is
        fully resolved.
        """

        # FIXME: Enable validation when we know how to skip it on South migrations
        #related_fields.add_lazy_relation(cls, self, self.rel.to, self._validate_relation)
        super(ReferenceChoiceField, self).contribute_to_class(cls, name, virtual_only=virtual_only)

    def value_from_object(self, obj):
        try:
            return getattr(obj, self.name)
        except models.ObjectDoesNotExist:
            return None

    def formfield(self, **kwargs):
        """
        Returns an augmented form field.
        """

        defaults = {
            'required': not self.blank,
            'label': text.capfirst(self.verbose_name),
            'help_text': self.help_text,
            'choices_model': self.rel.to,
        }

        return ReferenceChoiceFormField(**defaults)


class ReferenceChoiceFormField(form_fields.TypedChoiceField):
    """
    Form field for :class:`ReferenceChoiceField` database field.
    """

    def __init__(self, choices_model, *args, **kwargs):
        """
        Class constructor.

        :param choices_model: Choices model class
        """

        self.choices_rid = choices_model.get_registry_id()
        self.filter_model = choices_model
        self.partially_validated_tree = None
        super(ReferenceChoiceFormField, self).__init__(*args, **kwargs)

    def get_dependencies(self, value):
        """
        Returns a list of dependencies on other registry forms. This method will
        only be called when form validation succeeds and the form is scheduled
        to be saved.

        :param value: Cleaned value
        :return: A list of dependency tuples (cfg_location, cfg_parent, cfg_index)
        """

        if value is None:
            return []

        return [(self.choices_rid, None, value)]

    def modify_to_context(self, item, cfg, request):
        """
        Limits the valid choices to items from the partially validated configuration.
        """

        self.choices = [
            (index, model)
            for index, model in enumerate(cfg.get(self.choices_rid, []))
            if isinstance(model, self.filter_model)
        ]

        # Store the partially validated tree on which the choices are based
        self.partially_validated_tree = cfg

    def prepare_value(self, value):
        if isinstance(value, self.filter_model):
            for index, model in self.choices:
                if value.pk == model.pk:
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
        except (KeyError, IndexError, TypeError):
            return None

    def valid_value(self, value):
        if value is None:
            return True

        for index, model in self.choices:
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

# Add South introspection for our fields
south.modelsinspector.add_introspection_rules([
    (
        [SelectorKeyField],
        [],
        {
            'regpoint': ['regpoint', {}],
            'enum_id': ['enum_id', {}],
        },
    ),
], [r'^nodewatcher\.core\.registry\.fields\.SelectorKeyField$'])
south.modelsinspector.add_introspection_rules([], [r'^nodewatcher\.core\.registry\.fields\.ModelSelectorKeyField$'])
south.modelsinspector.add_introspection_rules([], [r'^nodewatcher\.core\.registry\.fields\.IntraRegistryForeignKey$'])
south.modelsinspector.add_introspection_rules([], [r'^nodewatcher\.core\.registry\.fields\.ReferenceChoiceField$'])
south.modelsinspector.add_introspection_rules([
    (
        [MACAddressField],
        [],
        {
            'auto_add': ['auto_add', {'default': False}],
        },
    ),
], [r'^nodewatcher\.core\.registry\.fields\.MACAddressField$'])
south.modelsinspector.add_introspection_rules([
    (
        [IPAddressField],
        [],
        {
            'subnet_required': ['subnet_required', {'default': False}],
            'host_required': ['host_required', {'default': False}],
        },
    ),
], [r'^nodewatcher\.core\.registry\.fields\.IPAddressField$'])
