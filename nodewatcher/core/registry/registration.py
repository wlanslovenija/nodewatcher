import collections

from django import apps as django_apps
from django.core import exceptions as django_exceptions
from django.db import models as django_models

import jsonfield

from . import access as registry_access, lookup as registry_lookup, state as registry_state
from . import exceptions
from ...utils import datastructures as nw_datastructures

bases = registry_state.bases


class Choice(object):
    def __init__(self, name, verbose_name, help_text=None, limited_to=None, icon=None, **kwargs):
        self.name = name
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.limited_to = limited_to
        self.icon = icon
        self.metadata = kwargs

    def get_field_tuple(self):
        return (self.name, self.verbose_name)

    def get_json(self):
        """
        Returns the choice suitable for JSON serialization.
        """

        output = self.metadata.copy()
        output.update({
            'name': self.name,
            'verbose_name': self.verbose_name,
            'help_text': self.help_text,
            'icon': self.icon,
        })
        return output

    def __repr__(self):
        return "<Choice '%s'>" % self.name


class LazyChoiceList(collections.Sequence):
    def __init__(self):
        super(LazyChoiceList, self).__init__()
        self._list = nw_datastructures.OrderedSet()
        self._dependent_choices = nw_datastructures.OrderedSet()
        self._returns_field_tuples = False

    def field_tuples(self):
        # Make a copy that shares the same list and dependencies but that changes
        # the way items are returned from this lazy list
        lazy_choices = LazyChoiceList()
        lazy_choices._list = self._list
        lazy_choices._dependent_choices = self._dependent_choices
        lazy_choices._returns_field_tuples = True
        return lazy_choices

    def get_json(self):
        """
        Returns a list of choices suitable for JSON serialization.
        """

        return [choice.get_json() for choice in self._list]

    def resolve(self, choice_name):
        """
        Resolves a choice name and returns a `Choice` descriptor. If the
        choice does not exist, `KeyError` is raised.

        :param choice_name: Choice name
        :return: An instance of `Choice`
        """

        for choice in self._list:
            if choice.name == choice_name:
                return choice

        raise KeyError(choice_name)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        if self._returns_field_tuples:
            return (choice.get_field_tuple() for choice in self._list.__iter__())
        else:
            return self._list.__iter__()

    def __getitem__(self, index):
        return list(self.__iter__())[index]

    def __nonzero__(self):
        return True

    def subset_choices(self, condition):
        return [
            (choice if not self._returns_field_tuples else choice.get_field_tuple())
            for limited_to, choice in self._dependent_choices
            if limited_to is None or condition(*limited_to)
        ]

    def add_choice(self, choice):
        self._dependent_choices.add((choice.limited_to, choice))
        self._list.add(choice)

    def remove_choice(self, choice_name):
        for limited_to, choice in self._dependent_choices:
            if choice.name == choice_name:
                self._dependent_choices.discard((limited_to, choice))
                break

        for choice in self._list:
            if choice.name == choice_name:
                self._list.discard(choice)
                break


class RegistrationPoint(object):
    """
    Registration point is a state holder for registry operations. There can be
    multiple registration points, each rooted at its own model.

    The registry has two hierarchies:
      - class hierarchy (static)
      - object hierarchy (runtime editable)
    """

    def __init__(self, model, namespace, point_id):
        """
        Class constructor.
        """

        self.model = model
        self.namespace = namespace
        self.name = point_id
        self.item_registry = {}
        self.item_classes = set()
        self.item_classes_name = {}
        self.item_object_toplevel = collections.OrderedDict()
        self.choices_registry = {}
        self.flat_lookup_proxies = {}

        self._form_defaults = []
        self._form_processors = []

    def _register_item_to_container(self, item, container):
        item_dict = container.setdefault(item._registry.registry_id, {})
        item_dict[item._meta.model_name] = item
        return collections.OrderedDict(
            sorted(container.items(), key=lambda x: x[1].values()[0]._registry.form_weight)
        )

    def _register_item(self, item, object_toplevel=True):
        """
        Common functions for registering an item for both simple items and hierarchical
        ones.
        """

        if not issubclass(item, self.item_base):
            raise TypeError("Not a valid registry item class!")

        # Sanity check for object names
        if '_' in item._meta.object_name:
            raise exceptions.InvalidRegistryItemName("Registry items must not have underscores in class names!")

        # Avoid registering the same class multiple times
        if item in self.item_classes:
            return False
        else:
            self.item_classes.add(item)
            self.item_classes_name['%s.%s' % (item._meta.app_label, item._meta.model_name)] = item

        # Record the item in object hierarchy so we know which items don't depend on any other items in the
        # object (runtime editable) hierarchy
        if object_toplevel:
            self.item_object_toplevel = self._register_item_to_container(item, self.item_object_toplevel)

        # Record the class with its registry identifier
        registry_id = item._registry.registry_id
        if item.__base__ == self.item_base:
            if registry_id in self.item_registry:
                raise exceptions.RegistryItemAlreadyRegistered(
                    "Multiple top-level registry items claim identifier '%s'! Claimed by '%s' and '%s'." % (
                        registry_id, self.item_registry[registry_id][0], item
                    )
                )
        elif registry_id not in self.item_registry:
            # Prevent registration of specializations when the top-level class has not yet been registered
            raise exceptions.RegistryItemNotRegistered(
                "Top-level registry class for '%s' not yet registered!" % registry_id
            )
        elif item._registry.hides_parent:
            parent = item.__base__
            parent._registry.hide_requests += 1

        # The first item in the list is the top-level class for this registry id
        self.item_registry.setdefault(registry_id, []).append(item)

        # Include registration point in item class.
        item._registry.registration_point = self

        return True

    def register_item(self, item):
        """
        Registers a new item to this registration point.
        """

        if not self._register_item(item):
            return

        # Register proxy fields for performing registry lookups.
        for field in item._registry.lookup_proxies:
            if isinstance(field, (tuple, list)):
                src_field, dst_fields = field
            else:
                src_field = dst_fields = field

            if not isinstance(dst_fields, (tuple, list)):
                dst_fields = (dst_fields,)

            for dst_field in dst_fields:
                # Ignore registrations of existing proxies.
                if dst_field in self.flat_lookup_proxies:
                    continue

                self.flat_lookup_proxies[dst_field] = item, src_field

    def register_subitem(self, parent, child):
        """
        Registers a registry item in a hierarchical relationship.
        """

        from . import fields as registry_fields

        # Verify parent registration
        if parent not in self.item_classes:
            raise django_exceptions.ImproperlyConfigured("Parent class '{0}' is not yet registered!".format(parent._meta.object_name))

        top_level = True

        # TODO: Perform validation for multiple defined intra registry foreign keys

        # Augment the item with hierarchy information, discover foreign keys
        for field in child._meta.fields:
            if isinstance(field, registry_fields.IntraRegistryForeignKey) and issubclass(parent, field.rel.to):
                if not field.null:
                    # Foreign key is required for this subitem, so it can't be a top-level item
                    top_level = False

                parent._registry.add_child_item(child, field)
                break
        else:
            raise django_exceptions.ImproperlyConfigured("Missing IntraRegistryForeignKey linkage for parent-child relationship!")

        # Register item with the registry
        self._register_item(child, top_level)

    def _unregister_item(self, item_cls):
        """
        A helper method for unregistering a single item.

        :param item_cls: Registry item class
        """

        parent = item_cls.__base__
        if item_cls._registry.hides_parent and parent != self.item_base:
            parent._registry.hide_requests -= 1

        self.item_classes.remove(item_cls)

    def unregister_item_by_name(self, cls_name):
        """
        Unregisters a previously registered item or subitem. If the class doesn't exist,
        this is silently ignored. See also `unregister_item`.

        :param cls_name: Registry item class name (with app label)
        """

        cls = self.item_classes_name.get(cls_name.lower(), None)
        if cls is None:
            return

        self.unregister_item(cls)

    def unregister_item(self, item_cls):
        """
        Unregisters a previously registered item or subitem. If the specified item
        defines the top-level schema item, all child items of this type will be unregistered.

        :param item_cls: Registry item class
        """

        if not issubclass(item_cls, self.item_base):
            raise TypeError("Specified class is not a valid registry item!")

        if item_cls not in self.item_classes:
            raise exceptions.RegistryItemNotRegistered("Registry item '%s' is not registered!" % item_cls._meta.object_name)

        registry_id = item_cls._registry.registry_id
        # TODO: Properly handle removal with new item list

        if item_cls.__base__ == self.item_base:
            removal = set()
            removal.update(self.item_registry[registry_id])
            removal.update(self.item_object_toplevel[registry_id].values())

            # Top-level item, remove all registered subclasses and subitems
            for item in removal:
                self._unregister_item(item)

            del self.item_object_toplevel[registry_id]
            del self.item_registry[registry_id]
        else:
            # Item that subclasses a top-level item
            del self.item_object_toplevel[registry_id][item_cls._meta.model_name]
            assert len(self.item_object_toplevel[registry_id]) > 0
            self._unregister_item(item_cls)

    def is_item(self, model):
        """
        Returns true if a specified model class is a registry item under this
        registration point.

        :param model: Model class
        """

        return issubclass(model, self.item_base)

    def get_children(self, parent=None, registry_id=None):
        """
        Returns the child registry item classes that are available under the given
        parent registry item (via internal foreign key relationships). If None is
        specified as `parent` then only registry items that are available at the
        topmost level are returned.

        :param parent: Parent registry item class or None
        """

        if parent is None:
            container = self.item_object_toplevel
        else:
            container = parent._registry.item_children

        if registry_id is None:
            return container.values()

        return container.get(registry_id, {}).copy()

    def get_top_level_queryset(self, root, registry_id):
        """
        Returns the queryset for fetching top-level items for the specific registry
        identifier.

        :param root: Instance of root class
        :param registry_id: A valid registry identifier
        :return: A tuple (queryset, top_class)
        """

        assert isinstance(root, self.model)
        try:
            top_level = self.item_registry[registry_id][0]
        except KeyError:
            raise exceptions.RegistryItemNotRegistered("Registry item with id '%s' is not registered!" % registry_id)

        return getattr(root, '{0}_{1}_{2}'.format(self.namespace, top_level._meta.app_label, top_level._meta.model_name)), top_level

    def get_top_level_class(self, registry_id):
        """
        Returns a top-level registry item class for a specific identifier.

        :param registry_id: A valid registry identifier
        """

        try:
            return self.item_registry[registry_id][0]
        except KeyError:
            raise exceptions.RegistryItemNotRegistered("Registry item with id '%s' is not registered!" % registry_id)

    def get_classes(self, registry_id):
        """
        Returns a list of classes registered under the specified identifier.

        :param registry_id: A valid registry identifier
        """

        try:
            return tuple(self.item_registry[registry_id])
        except KeyError:
            raise exceptions.RegistryItemNotRegistered("Registry item with id '%s' is not registered!" % registry_id)

    def get_class(self, registry_id, class_name):
        """
        Returns a class instance registered under specified registry identifier.

        :param registry_id: A valid registry identifier
        :param class_name: Case-insensitive class name
        :return: A valid class
        """

        for cls in self.get_classes(registry_id):
            if cls.__name__.lower() == class_name.lower():
                return cls

        raise exceptions.UnknownRegistryClass(class_name)

    def get_accessor(self, root):
        """
        Returns the registry accessor for the specified root.
        """

        assert isinstance(root, self.model)
        return getattr(root, self.namespace)

    def get_all_registry_ids(self):
        """
        Returns all known registry identifiers.
        """

        return self.item_registry.keys()

    def get_all_registry_items(self):
        """
        Returns all known registry items.
        """

        return self.item_registry.copy()

    def get_registered_choices(self, choices_id):
        """
        Returns a list of previously registered choice instances.
        """

        return self.choices_registry.setdefault(choices_id, LazyChoiceList())

    def get_lookup_proxy(self, field_name):
        """
        Returns a lookup proxy for a specific field (if one exists). If no proxy
        is registered under the specified name, a tuple of two None values is
        returned.

        :param field_name: Lookup proxy field name
        :return: A tuple (dst_model, dst_field) to the proxied model/field
        """

        return self.flat_lookup_proxies.get(field_name, (None, None))

    def get_model_with_field(self, registry_id, field):
        """
        Searches the class hierarchy under a specified registry identifier for a
        registry item that provides the specified field.

        :param registry_id: Registry identifier
        :param field: Field name
        :return: A tuple (model, field)
        """

        # Discover which model provides the destination field.
        for model in self.get_classes(registry_id):
            # Attempt to fetch the field from this model.
            try:
                dst_field = model._meta.get_field(field)
                # If the field exists we have found our model.
                return (model, dst_field)
            except django_models.FieldDoesNotExist:
                continue
        else:
            raise ValueError("No registry item under '%s' provides field '%s'!" % (registry_id, field))

    def register_choice(self, choices_id, choice):
        """
        Registers a new choice/enumeration.
        """

        if not isinstance(choice, Choice):
            raise TypeError("'choice' must be an instance of Choice!")

        self.get_registered_choices(choices_id).add_choice(choice)

    def unregister_choice(self, choices_id, choice_name):
        """
        Removes an existing choice/enumeration.
        """

        self.get_registered_choices(choices_id).remove_choice(choice_name)

    def config_items(self):
        """
        A generator that iterates through registered items.
        """

        return iter(self.item_classes)

    def registered_choices(self):
        """
        A generator that iterates through registered choices.
        """

        return self.choices_registry.iteritems()

    def add_mixins(self, *mixins):
        """
        Adds one or more mixins to the top-level registry item that is associated
        with this registration point.

        :param mixins: Mixin classes
        """

        self.item_base.__bases__ += tuple(mixins)

    # TODO: Should we support some kind of order specification?
    def add_form_defaults(self, defaults):
        """
        Adds a new form defaults setter.

        :param defaults: Form defaults instance or a list of instances
        """

        if not isinstance(defaults, list):
            defaults = [defaults]

        for default in defaults:
            if not hasattr(default, 'set_defaults'):
                raise TypeError("Form defaults instance should implement method 'set_defaults'.")

            self._form_defaults.append(default)

    def get_form_defaults(self):
        """
        Returns any form defaults setters.
        """

        return self._form_defaults

    def add_form_processor(self, processor, order=1000):
        """
        Adds a new form processor class.

        :param processor: Form processor class
        :param order: Optional order specifier (defaults to 1000)
        """

        self._form_processors.append({
            'order': order,
            'processor': processor,
        })

    def get_form_processors(self):
        """
        Returns any form processor classes.
        """

        return [p['processor'] for p in sorted(self._form_processors, key=lambda p: p['order'])]

    def get_root_metadata(self, root):
        try:
            return root.registry_metadata.get(self.namespace, {})
        except TypeError:
            return {}

    def set_root_metadata(self, root, metadata):
        if not root.registry_metadata:
            root.registry_metadata = {}

        root.registry_metadata[self.namespace] = metadata

    def __repr__(self):
        return "<RegistrationPoint '%s'>" % self.name


def remove_point(name):
    """
    Removes an existing registration point.

    :param name: Registration point name
    """

    p = point(name)
    # Unregister all models
    for models in p.get_all_registry_items().values():
        p.unregister_item(models[0])
    # Remove the registration point
    del registry_state.points[name]


def create_point(model, namespace, mixins=None):
    """
    Creates a new registration point (= registry root).

    :param model: Root model
    :param namespace: Registration point namespace
    :param mixins: Optional list of mixin classes for the top-level registry item
    """

    # Properly handle deferred root model names
    try:
        app_label, model_name = model.split('.')
    except ValueError:
        raise ValueError("Deferred root model names must be of the form app_label.model_name!")
    except AttributeError:
        app_label = model._meta.app_label
        model_name = model._meta.object_name

    point_id = '%s.%s' % (model_name.lower(), namespace)
    if point_id not in registry_state.points:
        point = RegistrationPoint(model, namespace, point_id)
        registry_state.points[point_id] = point

        # We import it here so that we can import this file
        # without an AppRegistryNotReady exception.
        from . import models as registry_models

        # Create a new top-level class
        class Meta(registry_models.RegistryItemBase.Meta):
            abstract = True

        if mixins is None:
            mixins = []

        base_name = '{0}{1}RegistryItem'.format(model_name, namespace.capitalize())
        item_base = type(
            base_name,
            (registry_models.RegistryItemBase,) + tuple(mixins),
            {
                '__module__': 'nodewatcher.core.registry.models',
                'Meta': Meta,
                'root': django_models.ForeignKey(
                    model, null=False, editable=False, related_name='{0}_%(app_label)s_%(class)s'.format(namespace)
                )
            }
        )
        point.item_base = item_base
        setattr(bases, base_name, item_base)

        def augment_root_model(model):
            # Augment the model with a custom manager and a custom accessor.
            model.add_to_class(namespace, registry_access.RegistryAccessor(point))
            if not isinstance(model.objects, registry_lookup.RegistryLookupManager):
                del model.objects
                model.add_to_class('objects', registry_lookup.RegistryLookupManager(point))
                model._default_manager = model.objects

            # Update the model attribute in regpoint instance.
            point.model = model

            # Add a registry metadata field to the root model.
            try:
                model._meta.get_field('registry_metadata')
            except django_exceptions.FieldDoesNotExist:
                model.add_to_class('registry_metadata', jsonfield.JSONField(default=dict, editable=False))

        # Try to load the model; if it is already loaded this will work, but if
        # not, we will need to defer part of object creation
        try:
            augment_root_model(django_apps.apps.get_registered_model(app_label, model_name))
        except LookupError:
            django_models.signals.class_prepared.connect(
                augment_root_model,
                sender='%s.%s' % (app_label, model_name),
            )


def point(name):
    """
    Returns an existing registration point.

    :param name: Registration point name
    """

    return registry_state.points[name]


def all_points():
    """
    Returns a list of all existing registration points.
    """

    return registry_state.points.values()


def register_form_for_item(item, form_class):
    """
    Registers a form for use with the specified registry item.

    :param item: Registry item class
    :param form_class: Form class
    """

    item._registry.set_form_class(form_class)


def register_serializer_for_item(item, serializer_class):
    """
    Registers a serializer for use with the specified registry item.

    :param item: Registry item class
    :param serializer_class: Serializer class
    """

    item._registry.serializer_class = serializer_class
