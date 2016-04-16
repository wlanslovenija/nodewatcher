import operator
import os

from django import db as django_db
from django.contrib.postgres import fields as postgres_fields
from django.core import exceptions
from django.db import models
from django.db.models import constants
from django.db.models.fields import related as related_fields
from django.forms import fields as widgets
from django.utils import text, functional
from django.utils.translation import ugettext_lazy as _

from ...utils import ipaddr

from . import registration
from .forms import fields as form_fields


class RegistryChoiceFieldMixin(object):
    def get_registered_choices(self):
        """
        Returns a reference to the registered choices object that this field
        uses to populate its list of choices.
        """

        return registration.point(self.regpoint).get_registered_choices(self.enum_id)

    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        Augments the containing class.
        """

        super(RegistryChoiceFieldMixin, self).contribute_to_class(cls, name, virtual_only)

        def get_FIELD_choice(self, field):
            value = getattr(self, field.attname)
            choices = registration.point(field.regpoint).get_registered_choices(field.enum_id)

            try:
                return choices.resolve(value)
            except KeyError:
                try:
                    return choices.resolve(field.default)
                except KeyError:
                    return None

        setattr(
            cls,
            'get_%s_choice' % self.name,
            functional.curry(get_FIELD_choice, field=self)
        )


class NullBooleanChoiceField(RegistryChoiceFieldMixin, models.NullBooleanField):
    """
    A null boolean field that is linked to a registered choice. For use in
    this field, registered choices should cover True/False/None values.
    """

    def __init__(self, regpoint, enum_id, *args, **kwargs):
        """
        Class constructor.
        """

        self.regpoint = regpoint
        self.enum_id = enum_id
        super(NullBooleanChoiceField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(NullBooleanChoiceField, self).deconstruct()
        args = [self.regpoint, self.enum_id] + args
        return name, path, args, kwargs


class RegistryChoiceField(RegistryChoiceFieldMixin, models.CharField):
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
        self._rp_choices = kwargs['choices'] = self.get_registered_choices().field_tuples()
        super(RegistryChoiceField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RegistryChoiceField, self).deconstruct()
        args = [self.regpoint, self.enum_id] + args
        return name, path, args, kwargs

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

        defaults['choices'] = self._rp_choices
        defaults['coerce'] = self.to_python
        if self.null:
            defaults['empty_value'] = None

        defaults.update(kwargs)
        return form_fields.RegistryChoiceFormField(**defaults)


class RegistryMultipleChoiceField(postgres_fields.ArrayField):

    def __init__(self, regpoint, enum_id, **kwargs):
        """
        Class constructor.
        """

        self.regpoint = regpoint
        self.enum_id = enum_id
        self._rp_choices = self.get_registered_choices().field_tuples()
        kwargs['base_field'] = models.CharField(max_length=50, choices=self._rp_choices)
        super(RegistryMultipleChoiceField, self).__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RegistryMultipleChoiceField, self).deconstruct()
        # Need to explicitly override path as ArrayField overwrites it. See Django ticket #24034.
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = []
        kwargs.update({
            'regpoint': self.regpoint,
            'enum_id': self.enum_id,
        })
        return name, path, args, kwargs

    def get_registered_choices(self):
        """
        Returns a reference to the registered choices object that this field
        uses to populate its list of choices.
        """

        return registration.point(self.regpoint).get_registered_choices(self.enum_id)

    # TODO: Check if we could combine this with RegistryChoiceField.
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

        defaults['choices'] = self._rp_choices
        defaults.update(kwargs)
        return form_fields.RegistryMultipleChoiceFormField(**defaults)


class ModelRegistryChoiceField(models.ForeignKey):
    """
    A standard foreign key that augments the resulting form widget with a special
    selector class that will cause the forms to be recomputed when this field is
    modified.
    """

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        if 'on_delete' not in kwargs:
            kwargs['on_delete'] = models.PROTECT
        super(ModelRegistryChoiceField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Returns an augmented form field.
        """

        defaults = {'widget': widgets.Select(attrs={'class': 'registry_form_selector'})}
        defaults.update(kwargs)
        return super(ModelRegistryChoiceField, self).formfield(**defaults)


class IntraRegistryRelatedObjectDescriptor(models.fields.related.ReverseManyToOneDescriptor):
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

    def deconstruct(self):
        name, path, args, kwargs = super(MACAddressField, self).deconstruct()
        if self.auto_add is not False:
            kwargs['auto_add'] = self.auto_add
            del kwargs['editable']
        return name, path, args, kwargs

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

        defaults = {'form_class': form_fields.MACAddressFormField}
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

    def deconstruct(self):
        name, path, args, kwargs = super(IPAddressField, self).deconstruct()
        if self.subnet_required is not False:
            kwargs['subnet_required'] = self.subnet_required
        if self.host_required is not False:
            kwargs['host_required'] = self.host_required
        return name, path, args, kwargs

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

        defaults = {'form_class': form_fields.IPAddressFormField}
        defaults.update(kwargs)
        return super(IPAddressField, self).formfield(**defaults)


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
        kwargs['on_delete'] = models.SET_NULL
        # We have our own limit_choices_to implementation.
        self._limit_choices_to = kwargs.pop('limit_choices_to', None)
        super(ReferenceChoiceField, self).__init__(*args, **kwargs)

    def _validate_relation(self, field, model, cls):
        """
        Performs relation validation after the destination model is fully resolved.
        """

        # We import it here so that we can import this file
        # without an AppRegistryNotReady exception.
        from . import models as registry_models

        if not issubclass(cls, registry_models.RegistryItemBase):
            raise exceptions.ImproperlyConfigured(
                'ReferenceChoiceField can only be used in registry item models!'
            )

        if not issubclass(self.rel.to, registry_models.RegistryItemBase):
            raise exceptions.ImproperlyConfigured(
                'ReferenceChoiceField requires a relation with a registry item!'
            )

        if cls._registry.registration_point != self.rel.to._registry.registration_point:
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
            'limit_choices_to': self._limit_choices_to,
        }

        return form_fields.ReferenceChoiceFormField(**defaults)


class RegistryProxySingleDescriptor(object):
    def __init__(self, field_with_rel):
        self.related = field_with_rel.rel.to
        self.cache_name = field_with_rel.get_cache_name()

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def get_queryset(self, **db_hints):
        db = django_db.router.db_for_read(self.related, **db_hints)
        return self.related._default_manager.using(db)

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is None:
            queryset = self.get_queryset().all()
        queryset._add_hints(instance=instances[0])

        rel_field = self.related._meta.get_field('root')
        rel_obj_attr = operator.attrgetter(rel_field.attname)
        instance_attr = lambda obj: obj._get_pk_val()
        instances_dict = dict((instance_attr(inst), inst) for inst in instances)
        queryset = queryset.filter(root__in=instances)

        if queryset.query.extra:
            # When there are extra queryset attributes to be set on the resulting instances,
            # we store them so that we can generate default objects with these attributes
            # set to None.
            for instance in instances:
                setattr(instance, '%s_extra' % self.cache_name, queryset.query.extra.keys())

        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        rel_obj_cache_name = rel_field.get_cache_name()
        for rel_obj in queryset:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            setattr(rel_obj, rel_obj_cache_name, instance)
        return queryset, rel_obj_attr, instance_attr, True, self.cache_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self

        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            try:
                rel_obj = self.get_queryset(instance=instance).get(root=instance)
            except self.related.DoesNotExist:
                rel_obj = None
            else:
                setattr(rel_obj, self.related._meta.get_field('root').get_cache_name(), instance)

            setattr(instance, self.cache_name, rel_obj)

        if rel_obj is None:
            # Create a default empty object.
            rel_obj = self.related()
            # Set any extra attributes required by the prefetch queryset to None. Otherwise
            # these attributes would simply not be there which could cause issues.
            for attr_name in getattr(instance, '%s_extra' % self.cache_name, []):
                setattr(rel_obj, attr_name, None)

        return rel_obj


class RegistryRelationField(models.Field):
    def __init__(self, to, *args, **kwargs):
        kwargs['rel'] = related_fields.ForeignObjectRel(self, to)
        super(RegistryRelationField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(RegistryRelationField, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, name, RegistryProxySingleDescriptor(self))


class RegistryProxyMultipleDescriptor(object):
    def __init__(self, field_with_rel):
        self.related_model = field_with_rel.rel.to
        self.related_field = field_with_rel.related_field
        self.cache_name = field_with_rel.get_cache_name()
        self.queryset = field_with_rel.queryset

        # Generate a chain that can be used to generate the filter query.
        toplevel = self.related_model._registry.get_toplevel_class()
        self.chain = ['%s_ptr' % x._meta.model_name for x in self.related_model._meta.get_base_chain(toplevel) or []]
        self.chain.append('root')

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.related_manager_cls(instance)

    @functional.cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's default
        # manager.
        superclass = self.related_model._default_manager.__class__
        rel_model = self.related_model
        rel_field = rel_model._meta.get_field('root')
        rel_subfield = self.related_field
        rel_queryset = self.queryset
        chain = constants.LOOKUP_SEP.join(self.chain)
        cache_name = self.cache_name

        class RelatedManager(superclass):
            def __init__(self, instance):
                super(RelatedManager, self).__init__()
                self.instance = instance
                self.core_filters = {chain: instance}
                self.model = rel_model

            def __call__(self, **kwargs):
                raise Exception

            def _get_queryset(self):
                if rel_queryset is not None:
                    # If a queryset is available, use it instead of the default queryset as it may have
                    # some additional constraints applied.
                    return rel_queryset.all()
                else:
                    return super(RelatedManager, self).get_queryset()

            def get_queryset(self):
                try:
                    qs = self.instance._prefetched_objects_cache[cache_name]
                except (AttributeError, KeyError):
                    db = self._db or django_db.router.db_for_read(self.model, instance=self.instance)
                    empty_strings_as_null = django_db.connections[db].features.interprets_empty_strings_as_nulls
                    qs = self._get_queryset()

                    qs._add_hints(instance=self.instance)
                    if self._db:
                        qs = qs.using(self._db)
                    qs = qs.filter(**self.core_filters)

                    for field in rel_field.foreign_related_fields:
                        val = getattr(self.instance, field.attname)
                        if val is None or (val == '' and empty_strings_as_null):
                            return qs.none()
                    qs._known_related_objects = {rel_field: {self.instance.pk: self.instance}}

                if rel_subfield is not None:
                    return qs.values_list(rel_subfield, flat=True)

                return qs

            def get_prefetch_queryset(self, instances, queryset=None):
                if queryset is None:
                    queryset = self._get_queryset()

                queryset._add_hints(instance=instances[0])
                queryset = queryset.using(queryset._db or self._db)

                rel_obj_attr = operator.attrgetter(rel_field.attname)
                instance_attr = lambda obj: obj._get_pk_val()
                instances_dict = dict((instance_attr(inst), inst) for inst in instances)
                queryset = queryset.filter(**{'%s__in' % chain: instances})

                # Since we just bypassed this class' get_queryset(), we must manage
                # the reverse relation manually.
                for rel_obj in queryset:
                    instance = instances_dict[rel_obj_attr(rel_obj)]
                    setattr(rel_obj, rel_field.name, instance)

                return queryset, rel_obj_attr, instance_attr, False, cache_name

        return RelatedManager


class RegistryMultipleRelationField(models.Field):
    def __init__(self, to, *args, **kwargs):
        self.related_field = kwargs.pop('related_field', None)
        self.queryset = kwargs.pop('queryset', None)
        kwargs['rel'] = related_fields.ForeignObjectRel(self, to)
        super(RegistryMultipleRelationField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(RegistryMultipleRelationField, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, name, RegistryProxyMultipleDescriptor(self))
