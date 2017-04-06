import copy
import inspect

from django import db as django_db
from django.apps import apps
from django.core import exceptions as django_exceptions
from django.db import models as django_models
from django.db.models import constants
from django.utils import tree

from . import expression, exceptions


class RegistryQuerySet(django_models.QuerySet):
    """
    An augmented query set that enables lookups of values from the registry.
    """

    def __init__(self, *args, **kwargs):
        super(RegistryQuerySet, self).__init__(*args, **kwargs)

        # Quote name. We import it here so that we can import this file
        # without an AppRegistryNotReady exception.
        self._quote_name = django_db.connection.ops.quote_name

    def _clone(self, *args, **kwargs):
        """
        Clones this queryset.
        """

        clone = super(RegistryQuerySet, self)._clone(*args, **kwargs)
        clone._regpoint = getattr(self, '_regpoint', None)
        return clone

    def regpoint(self, name):
        """
        Switches to a different regpoint that determines the short attribute
        name.
        """

        from . import registration
        clone = self._clone()
        try:
            name = '{0}.{1}'.format(self.model._meta.concrete_model._meta.model_name, name)
            clone._regpoint = registration.point(name)
            return clone
        except KeyError:
            raise ValueError("Registration point '{0}' does not exist!".format(name))

    def registry_filter(self, **kwargs):
        """
        An augmented filter that enables filtering by virtual aliases for
        registry fields via joins.
        """

        disallow_sensitive = kwargs.pop('disallow_sensitive', False)

        if getattr(self, '_regpoint', None) is None:
            raise ValueError("Calling 'registry_filter' first requires a selected registration point!")

        clone = self._clone()

        # Resolve fields from kwargs that are virtual aliases for registry fields
        filter_selectors = {}
        ensure_distinct = False
        for selector, value in kwargs.items():
            if constants.LOOKUP_SEP in selector:
                field, selector = selector.split(constants.LOOKUP_SEP, 1)
            else:
                field = selector
                selector = None

            # First check if there is a flat lookup proxy
            dst_model, dst_field = self._regpoint.get_lookup_proxy(field)
            if dst_model is None:
                if selector is None:
                    raise ValueError("'%s' is not a known proxy field!" % field)
                else:
                    # Not a lookup proxy, check if this is a valid registry identifier
                    registry_id = field.replace('_', '.')
                    if constants.LOOKUP_SEP in selector:
                        dst_field, selector = selector.split(constants.LOOKUP_SEP, 1)
                    else:
                        dst_field = selector
                        selector = None

                    dst_model, dst_field = self._regpoint.get_model_with_field(registry_id, dst_field)
                    dst_field = dst_field.name

            # Disallow filter by sensitive fields if requested.
            if dst_field in dst_model._registry.sensitive_fields and disallow_sensitive:
                continue

            if dst_model._registry.multiple:
                ensure_distinct = True

            new_selector = dst_model._registry.get_lookup_chain() + constants.LOOKUP_SEP + dst_field
            if selector is not None:
                new_selector += constants.LOOKUP_SEP + selector

            filter_selectors[new_selector] = value

        # Pass transformed query into the standard filter routine.
        clone = super(RegistryQuerySet, clone).filter(**filter_selectors)
        if ensure_distinct:
            clone = clone.distinct()
        return clone

    def registry_expand_proxy_field(self, alias):
        """
        Expands a proxy virtual field previously setup by registry_fields into a field
        path suitable for use in filters. In case the alias is a standard Django field or
        a path of such fields, it is returned unmodified.

        :param alias: Alias field name or a path starting with such a field
        """

        raw_alias = alias
        alias = alias.split(constants.LOOKUP_SEP)
        base_alias = alias[0]

        try:
            field = self.model._meta.get_field(base_alias)
        except django_models.FieldDoesNotExist:
            for f in self.model._meta.virtual_fields:
                field = f
                if field.name == base_alias:
                    break
            else:
                # When a field cannot be resolved, return the alias unchanged.
                return raw_alias

        src_model = getattr(field, 'src_model', None)
        if src_model is not None:
            if field.src_field is None and len(alias) > 1:
                # We need to perform model resolution again as the destination model
                # is not known as a field name is required to resolve the proper model subclass.
                src_model = src_model._registry.registration_point.get_model_with_field(
                    src_model._registry.registry_id, alias[1]
                )[0]

            selector = [src_model._registry.get_lookup_chain()]
            if field.src_field is not None:
                selector.append(field.src_field)
            if alias[1:]:
                selector += alias[1:]

            return constants.LOOKUP_SEP.join(selector)

        return raw_alias

    def raw_filter(self, *args, **kwargs):
        return super(RegistryQuerySet, self).filter(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """
        An augmented filter method to support querying by virtual fields created
        by registry_fields.
        """

        clone = self._clone()

        def process_q(node):
            for index, child in enumerate(node.children):
                if isinstance(child, tree.Node):
                    process_q(child)
                else:
                    try:
                        selector, value = child
                    except ValueError:
                        continue

                    node.children[index] = (
                        self.registry_expand_proxy_field(selector),
                        value
                    )

        q_selectors = []
        for q_selector in args:
            if isinstance(q_selector, django_models.Q):
                process_q(q_selector)
            q_selectors.append(q_selector)

        filter_selectors = {}
        for selector, value in kwargs.items():
            filter_selectors[self.registry_expand_proxy_field(selector)] = value

        return super(RegistryQuerySet, clone).filter(*q_selectors, **filter_selectors)

    def exclude(self, *args, **kwargs):
        """
        An augmented exclude method to support querying by virtual fields created
        by registry_fields.
        """

        clone = self._clone()

        exclude_selectors = {}
        for selector, value in kwargs.items():
            exclude_selectors[self.registry_expand_proxy_field(selector)] = value

        return super(RegistryQuerySet, clone).exclude(*args, **exclude_selectors)

    def registry_fields(self, **kwargs):
        """
        Select fields from the registry.
        """

        from . import registration

        clone = self._clone()

        # Construct a temporary fake model for this query.
        if not hasattr(clone.model, '_registry_proxy'):
            # Clear any existing proxy models to prevent duplicate class warnings.
            try:
                del apps.all_models['_registry_proxy_models_']
            except KeyError:
                pass

            class Meta:
                proxy = True
                app_label = '_registry_proxy_models_'

            # Use a dictionary to transfer data to closure by reference.
            this_class = {'parent': clone.model}

            def pickle_reduce(self):
                t = super(this_class['class'], self).__reduce__()
                attrs = t[2]
                for name in self._registry_attrs:
                    if name in attrs:
                        del attrs[name]
                return (t[0], (this_class['parent'], t[1][1], t[1][2]), attrs)

            clone.model = type(
                '%sRegistryProxy' % clone.model.__name__,
                (clone.model,),
                {
                    '__module__': 'nodewatcher.core.registry.lookup',
                    '_registry_proxy': True,
                    '_registry_attrs': [],
                    'Meta': Meta,
                    '__reduce__': pickle_reduce,
                },
            )
            clone.query.model = clone.model
            this_class['class'] = clone.model

        def install_proxy_field(model, field, name, src_model=None, src_field=None):
            field = copy.deepcopy(field)
            field.name = None
            # Include src_model and src_field to enable destination field resolution.
            field.src_model = src_model
            field.src_field = src_field
            select_name = name
            # Since the field is populated by a join, it can always be null when the model doesn't exist
            field.null = True
            field.contribute_to_class(clone.model, name, virtual_only=True)
            field.concrete = False

            if field.is_relation:
                # Handle foreign key relations properly.
                select_name = '%s_att' % name
                field.attname = select_name

                # Clear field cache to ensure the correct field is used to determine attname.
                if hasattr(field, '_related_fields'):
                    del field._related_fields

            model._registry_attrs.append(select_name)
            return select_name

        parser = expression.LookupExpressionParser()
        for field_name, dst in kwargs.iteritems():
            info = None
            dst_queryset = None
            dst_field = None
            dst_related = None
            m2m = False

            if inspect.isclass(dst) and issubclass(dst, django_models.Model):
                dst_model = dst
            elif isinstance(dst, django_models.QuerySet):
                dst_model = dst.model
                dst_queryset = dst
            else:
                if isinstance(dst, expression.LookupExpression):
                    # We can use an already parsed lookup expression directly.
                    info = dst
                else:
                    info = parser.parse(dst)

                try:
                    if not info.registration_point:
                        registration_point = self._regpoint
                        if not registration_point:
                            raise ValueError("Registration point not specified.")
                    else:
                        registration_point = registration.point('%s.%s' % (clone.model._meta.concrete_model._meta.model_name, info.registration_point))
                except KeyError, name:
                    raise ValueError("Invalid registration point: %s" % name)

                if info.field:
                    # Discover, which model provides the destination field.
                    dst_model, dst_field = registration_point.get_model_with_field(info.registry_id, info.field[0])
                    m2m = dst_field.many_to_many

                    # TODO: Support arbitrary chains of relations.
                    if len(info.field) > 1:
                        dst_related = info.field[1]
                else:
                    dst_model = registration_point.get_top_level_class(info.registry_id)

                # If there are constraints, we need to specify a queryset and apply the constraints.
                if info.constraints:
                    dst_queryset = info.apply_constraints(dst_model.objects.all())

            if not hasattr(dst_model, '_registry'):
                raise TypeError("Specified model must be a registry item.")
            if not issubclass(clone.model, dst_model._registry.registration_point.model):
                raise TypeError("Specified registry item is not part of any registration point for '%s'." % clone.model.__name__)
            if m2m:
                raise ValueError("Many-to-many fields not supported in registry_fields query!")

            if dst_model._registry.multiple:
                # The destination model can contain multiple items; in this case we need to
                # provide the proxy model with a descriptor that returns a queryset to the models.
                if dst_related is not None:
                    raise ValueError("Related fields on registry items with multiple models not supported!")
                if dst_field is not None and not dst_field.concrete:
                    raise ValueError("Cannot project non-concrete field on registry items with multiple models.")

                from . import fields

                dst_field_name = dst_field.name if dst_field else None
                field = fields.RegistryMultipleRelationField(dst_model, related_field=dst_field_name, queryset=dst_queryset)
                field.src_model = dst_model
                field.src_field = dst_field_name
                field.contribute_to_class(clone.model, field_name, virtual_only=True)
                field.concrete = False
                clone = clone.prefetch_related(django_models.Prefetch(field_name, queryset=dst_queryset))
                continue
            elif dst_field is None:
                # If there can only be one item and no field is requested, create a descriptor.
                from . import fields

                field = fields.RegistryRelationField(dst_model)
                # Add proxy attributes so that the field can be used in filter.
                field.src_model = dst_model
                field.src_field = None
                field.contribute_to_class(clone.model, field_name, virtual_only=True)
                field.concrete = False
                clone = clone.prefetch_related(django_models.Prefetch(field_name, queryset=dst_queryset))
                continue
            elif dst_related is None:
                # Select destination field and install proxy field descriptor.
                # TODO: Support prefetching if dst_field.is_relation is True.
                src_column = '%s.%s' % (self._quote_name(dst_model._meta.db_table), self._quote_name(dst_field.column))
                select_name = install_proxy_field(
                    clone.model,
                    dst_field,
                    field_name,
                    src_model=dst_model,
                    src_field=dst_field.name,
                )
                clone = clone.extra(select={select_name: src_column})
            else:
                # Traverse the relation and copy the destination field descriptor.
                dst_field_model = dst_field.rel.to
                dst_related_field = dst_field_model._meta.get_field(dst_related)

                # TODO: Support arbitrary chain of relations

                if dst_related_field.many_to_many:
                    raise ValueError("Many-to-many fields not supported in registry_fields query!")

                src_column = '%s.%s' % (self._quote_name(dst_field_model._meta.db_table), self._quote_name(dst_related_field.column))
                select_name = install_proxy_field(
                    clone.model,
                    dst_related_field,
                    field_name,
                    src_model=dst_model,
                    src_field=constants.LOOKUP_SEP.join((dst_field.name, dst_related))
                )
                clone = clone.extra(select={select_name: src_column})

            # Setup required joins.
            field_names = clone.registry_expand_proxy_field(field_name).split(constants.LOOKUP_SEP)
            clone.query.setup_joins(field_names, clone.model._meta, clone.query.get_initial_alias())

        return clone

    def raw_order_by(self, *args, **kwargs):
        return super(RegistryQuerySet, self).order_by(*args, **kwargs)

    def order_by(self, *fields, **kwargs):
        """
        Order by registry fields.
        """

        return order_by(
            self,
            fields,
            self.model,
            disallow_sensitive=kwargs.pop('disallow_sensitive', False),
        )


class RegistryLookupManager(django_models.Manager):
    """
    A manager for doing lookups over the registry models.
    """

    def __init__(self, regpoint=None):
        """
        Class constructor.

        :param regpoint: Registration point instance
        """

        self._regpoint = regpoint
        super(RegistryLookupManager, self).__init__()

    def get_queryset(self):
        qs = RegistryQuerySet(self.model, using=self._db)
        if self._regpoint is not None:
            qs._regpoint = self._regpoint
        return qs

    def regpoint(self, name):
        return self.get_queryset().regpoint(name)

    def registry_fields(self, **kwargs):
        return self.get_queryset().registry_fields(**kwargs)


def selector_for_lookup(root_cls, lookup, disallow_sensitive=False):
    """
    Generates a Django ORM selector for performing a specific registry field lookup.

    :param root_cls: Registry root model class
    :param lookup: A LookupExpression for the destination field
    :param disallow_sensitive: Should sensitive fields be disallowed
    :return A tuple (selector, field, ensure_distinct) or None in case a field is disallowed
    """

    from . import registration

    registration_point = registration.point('{}.{}'.format(
        root_cls._meta.concrete_model._meta.model_name,
        lookup.registration_point
    ))
    dst_model, dst_field = registration_point.get_model_with_field(
        lookup.registry_id,
        lookup.field[0]
    )

    # Disallow filter by sensitive fields if requested.
    if dst_field.name in dst_model._registry.sensitive_fields and disallow_sensitive:
        return None

    selector = dst_model._registry.get_lookup_chain() + constants.LOOKUP_SEP + dst_field.name
    if len(lookup.field) > 1:
        selector += constants.LOOKUP_SEP + constants.LOOKUP_SEP.join(lookup.field[1:])

    ensure_distinct = dst_model._registry.multiple
    return (selector, dst_field, ensure_distinct)


def order_by(queryset, ordering, root_cls, field=None, disallow_sensitive=False):
    """
    Orders a queryset using registry field specifiers.
    """

    from . import fields as registry_fields

    ordering_specifiers = []
    parser = expression.LookupExpressionParser()
    for field_specifier in ordering:
        if field_specifier[0] == '-':
            order = '-'
            field_specifier = field_specifier[1:]
        else:
            order = ''

        try:
            info = parser.parse(field_specifier)

            # Use default registration point for registry querysets.
            if not info.registration_point and hasattr(queryset, '_regpoint'):
                info.registration_point = queryset._regpoint.namespace
        except (exceptions.RegistryItemNotRegistered, django_exceptions.FieldError, ValueError):
            continue

        # Pass-through field by default.
        selector = None

        if info.field:
            # Valid registry field.
            try:
                selector, dst_field, _ = selector_for_lookup(root_cls, info, disallow_sensitive=disallow_sensitive)
            except TypeError:
                # Disallowed field.
                continue
            except exceptions.RegistryItemNotRegistered:
                pass

        if selector is None:
            if hasattr(queryset, 'registry_expand_proxy_field'):
                # Non-registry field or an alias.
                selector = queryset.registry_expand_proxy_field(field_specifier)
            else:
                # Pass-through field.
                selector = field_specifier

        # Add subfield prefix if required.
        if field is not None:
            selector = field.name + constants.LOOKUP_SEP + selector

        dst_field = queryset.query.names_to_path(
            selector.split(constants.LOOKUP_SEP),
            queryset.model._meta,
            fail_on_missing=True
        )[1]

        # Ordering by registry choice fields should generate a specific query that will sort by the
        # order that the choices were registered, instead of by their value.
        if isinstance(dst_field, (registry_fields.RegistryChoiceField, registry_fields.NullBooleanChoiceField)):
            cases = []
            for order, choice in enumerate(dst_field.get_registered_choices()):
                cases.append(django_models.When(
                    then=django_models.Value(order),
                    **{selector: choice.name}
                ))

            order_field = django_models.Case(*cases, output_field=django_models.IntegerField())
            if order == '-':
                order_field = order_field.desc()
            else:
                order_field = order_field.asc()
        else:
            order_field = '{}{}'.format(order, selector)

        ordering_specifiers.append(order_field)

    if hasattr(queryset, 'raw_order_by'):
        return queryset.raw_order_by(*ordering_specifiers)
    else:
        return queryset.order_by(*ordering_specifiers)
