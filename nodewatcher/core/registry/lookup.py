import copy

from django.contrib.gis.db import models as gis_models
from django import db as django_db
from django.db.models.sql import constants
from django.utils import functional

from . import access as registry_access, exceptions

# Quote name
qn = django_db.connection.ops.quote_name


class RegistryProxyMixin(object):
    # TODO: Needed until Django 1.7, see https://code.djangoproject.com/ticket/16458
    def __eq__(self, other):
        return (isinstance(other, django_db.models.Model) and
                self._meta.concrete_model == other._meta.concrete_model and
                self._get_pk_val() == other._get_pk_val())


class RegistryProxySingleDescriptor(object):
    def __init__(self, related_model):
        self.related_model = related_model

    def __get__(self, instance, instance_type):
        if instance is None:
            return self

        return self.related_model.objects.get(root=instance)


class RegistryProxyMultipleDescriptor(object):
    def __init__(self, related_model, chain, related_field=None):
        self.related_model = related_model
        self.related_field = related_field
        self.chain = chain

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        if self.related_field is not None:
            chain = "__".join(self.chain + ['root'])
            qs = self.related_model.objects.filter(**{chain: instance})
            qs = qs.values_list(self.related_field, flat=True)
            return list(qs)

        return self.related_manager_cls(instance)

    @functional.cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's default
        # manager.
        superclass = self.related_model._default_manager.__class__
        rel_model = self.related_model
        chain = "__".join(self.chain + ['root'])

        class RelatedManager(superclass):
            def __init__(self, instance):
                super(RelatedManager, self).__init__()
                self.instance = instance
                self.core_filters = {chain: instance}
                self.model = rel_model

            def get_query_set(self):
                db = self._db or django_db.router.db_for_read(self.model, instance=self.instance)
                return super(RelatedManager, self).get_query_set().using(db).filter(**self.core_filters)

        return RelatedManager


class RegistryQuerySet(gis_models.query.GeoQuerySet):
    """
    An augmented query set that enables lookups of values from the registry.
    """

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
            name = '{0}.{1}'.format(self.model._meta.concrete_model._meta.module_name, name)
            clone._regpoint = registration.point(name)
            return clone
        except KeyError:
            raise ValueError("Registration point '{0}' does not exist!".format(name))

    def filter(self, **kwargs):
        """
        An augmented filter that enables filtering by virtual aliases for
        registry fields via joins.
        """

        if not hasattr(self, '_regpoint'):
            return super(RegistryQuerySet, self).filter(**kwargs)

        clone = self._clone()

        # Resolve fields from kwargs that are virtual aliases for registry fields
        for condition, value in kwargs.items():
            if '__' in condition:
                field = condition[:condition.find('__')]
            else:
                field = condition

            # First check if there is a flat lookup proxy
            dst_model, dst_field = self._regpoint.flat_lookup_proxies.get(field, (None, None))
            if dst_model is None and '_' in field:
                dst_model, dst_field = field.split('_', 1)
                try:
                    dst_model = registry_access.get_model_class_by_name(dst_model)
                except exceptions.UnknownRegistryClass:
                    dst_model = None

            if dst_model is not None:
                dst_field = dst_model.lookup_path() + '__' + dst_field
                del kwargs[condition]
                condition = condition.replace(field, dst_field)
                kwargs[condition] = value

        # Pass transformed query into the standard filter routine
        return super(RegistryQuerySet, clone).filter(**kwargs)

    def registry_fields(self, **kwargs):
        """
        Select fields from the registry.
        """

        clone = self._clone()

        # Construct a temporary fake model for this query
        if not hasattr(clone.model, '_registry_proxy'):
            class Meta:
                proxy = True
                app_label = '_registry_proxy_models_'

            # Use a dictionary to transfer data to closure by reference
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
                (RegistryProxyMixin, clone.model),
                {
                    '__module__': 'nodewatcher.core.registry.lookup',
                    '_registry_proxy': True,
                    '_registry_attrs': [],
                    'Meta': Meta,
                    '__reduce__': pickle_reduce,
                },
            )
            this_class['class'] = clone.model

            # Prevent proxy models from cluttering up the cache
            del django_db.models.loading.cache.app_models['_registry_proxy_models_']
            # All our fields are virtual
            clone.model._meta.add_field = clone.model._meta.add_virtual_field

        def install_proxy_field(model, field, name):
            field = copy.deepcopy(field)
            field.name = None
            select_name = name
            # Since the field is populated by a join, it can always be null when the model doesn't exist
            field.null = True
            field.contribute_to_class(clone.model, name)

            if field.name != field.attname:
                # Handle foreign key relations properly
                select_name = '%s_att' % name
                field.attname = select_name

            model._registry_attrs.append(select_name)
            return select_name

        for field_name, dst in kwargs.iteritems():
            if '#' in dst:
                try:
                    dst_registry_id, dst_field = dst.split('#')
                except ValueError:
                    raise ValueError("Expecting 'registry.id#field' specifier instead of '%s'!" % dst)

                # Dots in field specify relation traversal
                if '.' in dst_field:
                    # TODO: Support arbitrary chain of relations
                    dst_field, dst_related = dst_field.split('.')
                else:
                    dst_related = None

                # Discover which model provides the destination field
                dst_model = None
                for model in self._regpoint.get_classes(dst_registry_id):
                    # Attempt to fetch the field from this model
                    try:
                        field, _, _, m2m = model._meta.get_field_by_name(dst_field)
                        # If the field exists we have found our model
                        dst_model = model
                        dst_field = field
                        break
                    except django_db.models.FieldDoesNotExist:
                        continue
                else:
                    raise ValueError("No registry item under '%s' provides field '%s'!" % (dst_registry_id, dst_field))
            else:
                dst_registry_id = dst
                dst_model = self._regpoint.get_top_level_class(dst_registry_id)
                dst_field = None
                dst_related = None
                m2m = False

            if m2m:
                raise ValueError("Many-to-many fields not supported in registry_fields query!")

            if dst_model.has_registry_multiple():
                # The destination model can contain multiple items; in this case we need to
                # provide the proxy model with a descriptor that returns a queryset to the models
                if dst_related is not None:
                    raise ValueError("Related fields on registry items with multiple models not supported!")

                # Generate a chain that can be used to generate the filter query
                toplevel = dst_model.get_registry_toplevel()
                chain = ['%s_ptr' for x in dst_model._meta.get_base_chain(toplevel) or []]
                setattr(clone.model, field_name, RegistryProxyMultipleDescriptor(dst_model, chain, dst_field.name if dst_field else None))
                continue

            if dst_field is None:
                # If there can only be one item and no field is requested, create a descriptor
                setattr(clone.model, field_name, RegistryProxySingleDescriptor(dst_model))
                continue
            elif dst_related is None:
                # Select destination field and install proxy field descriptor
                select_name = install_proxy_field(clone.model, dst_field, field_name)
                clone = clone.extra(select={select_name: '%s.%s' % (qn(dst_model._meta.db_table), qn(dst_field.column))})
            else:
                # Traverse the relation and copy the destination field descriptor
                dst_field_model = dst_field.rel.to
                dst_related_field, _, _, m2m = dst_field_model._meta.get_field_by_name(dst_related)

                # TODO: Support arbitrary chain of relations

                if m2m:
                    raise ValueError("Many-to-many fields not supported in registry_fields query!")

                select_name = install_proxy_field(clone.model, dst_related_field, field_name)
                clone = clone.extra(select={select_name: '%s.%s' % (qn(dst_field_model._meta.db_table), qn(dst_related_field.column))})

            clone.query.get_initial_alias()

            # Join with top-level item
            toplevel = dst_model.get_registry_toplevel()
            clone.query.join(
                (self.model._meta.db_table, toplevel._meta.db_table, self.model._meta.pk.column, 'root_id'),
                promote=True,
            )

            if toplevel != dst_model:
                # Join with lower-level item
                clone.query.join(
                    (toplevel._meta.db_table, dst_model._meta.db_table, toplevel._meta.pk.column, dst_model._meta.pk.column),
                    promote=True,
                )

            if dst_related is not None:
                dst_field_model = dst_field.rel.to
                clone.query.join(
                    (dst_model._meta.db_table, dst_field_model._meta.db_table, dst_field.column, dst_field_model._meta.pk.column),
                    promote=True,
                )

        return clone

    def ip_filter(self, **kwargs):
        """
        Performs a lookup on inet fields.
        """

        connection = django_db.connections[self._db or django_db.DEFAULT_DB_ALIAS]
        where_opts = []
        for key, value in kwargs.iteritems():
            field, op = key.split(constants.LOOKUP_SEP)
            field_obj = self.model._meta.get_field_by_name(field)[0]
            value = field_obj.get_db_prep_lookup('exact', value, connection=connection)[0]
            field = '%s.%s' % (self.model._meta.db_table, field)

            if op == 'contains':
                where_opts.append('%s >>= %s' % (field, value))
            elif op == 'contained':
                where_opts.append('%s <<= %s' % (field, value))
            elif op == 'conflicts':
                where_opts.append('(%s <<= %s OR %s >>= %s)' % (field, value, field, value))
            else:
                raise TypeError("Operation '%s' not supported." % op)

        return self.extra(where=where_opts)


class RegistryLookupManager(gis_models.GeoManager):
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

    def get_query_set(self):
        qs = RegistryQuerySet(self.model, using=self._db)
        if self._regpoint is not None:
            qs._regpoint = self._regpoint
        return qs

    def regpoint(self, name):
        return self.get_query_set().regpoint(name)

    def registry_fields(self, **kwargs):
        return self.get_query_set().registry_fields(**kwargs)
