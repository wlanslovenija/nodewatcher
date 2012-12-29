import collections

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import datastructures as django_datastructures

from nodewatcher.core.registry import state as registry_state
from nodewatcher.core.registry import models as registry_models
from nodewatcher.core.registry import lookup as registry_lookup
from nodewatcher.core.registry import access as registry_access
from nodewatcher.utils import datastructures as nw_datastructures

bases = registry_state.bases

class LazyChoiceList(collections.Sequence):
    def __init__(self):
        super(LazyChoiceList, self).__init__()
        self._list = nw_datastructures.OrderedSet()
        self._dependent_choices = nw_datastructures.OrderedSet()

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return self._list.__iter__()

    def __getitem__(self, index):
        return list(self._list)[index]

    def __nonzero__(self):
        return True

    def subset_choices(self, condition):
        return [choice for limited_to, choice in self._dependent_choices if limited_to is None or condition(*limited_to)]

    def add_choice(self, choice, limited_to):
        self._dependent_choices.add((limited_to, choice))
        self._list.add(choice)

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
        self.item_object_toplevel = django_datastructures.SortedDict()
        self.choices_registry = {}
        self.flat_lookup_proxies = {}

    def _register_item_to_container(self, item, container):
        item_dict = container.setdefault(item.RegistryMeta.registry_id, {})
        item_dict[item._meta.module_name] = item
        return django_datastructures.SortedDict(
          sorted(container.items(), key = lambda x: getattr(x[1].values()[0].RegistryMeta, 'form_order', 0))
        )

    def _register_item(self, item, object_toplevel = True):
        """
        Common functions for registering an item for both simple items and hierarchical
        ones.
        """
        if not issubclass(item, self.item_base):
            raise TypeError("Not a valid registry item class!")

        # Sanity check for object names
        if '_' in item._meta.object_name:
            raise ImproperlyConfigured("Registry items must not have underscores in class names!")

        # Avoid registering the same class multiple times
        if item in self.item_classes:
            return False
        else:
            self.item_classes.add(item)

        # Record the item in object hierarchy so we know which items don't depend on any other items in the
        # object (runtime editable) hierarchy
        if object_toplevel:
            self.item_object_toplevel = self._register_item_to_container(item, self.item_object_toplevel)

        # Only record the top-level item (class hierarchy) in the registry as there could be multiple
        # specializations that define their own extensions
        if item.__base__ == self.item_base:
            registry_id = item.RegistryMeta.registry_id
            if registry_id in self.item_registry:
                raise ImproperlyConfigured(
                  "Multiple top-level registry items claim identifier '{0}'! Claimed by '{1}' and '{2}'.".format(
                    registry_id, self.item_registry[registry_id], item
                ))

            self.item_registry[registry_id] = item
        elif getattr(item.RegistryMeta, 'hides_parent', False):
            parent = item.__base__
            parent._registry_hide_requests += 1

        # Include registration point in item class
        item._registry_regpoint = self
        item._registry_hide_requests = 0

        return True

    def register_item(self, item):
        """
        Registers a new item to this registration point.
        """
        if not self._register_item(item):
            return

        # Register proxy fields for performing registry lookups
        lookup_proxies = getattr(item.RegistryMeta, 'lookup_proxies', None)
        if lookup_proxies is not None:
            for field in lookup_proxies:
                if isinstance(field, (tuple, list)):
                    src_field, dst_fields = field
                else:
                    src_field = dst_fields = field

                if not isinstance(dst_fields, (tuple, list)):
                    dst_fields = (dst_fields,)

                for dst_field in dst_fields:
                    # Ignore registrations of existing proxies
                    if dst_field in self.flat_lookup_proxies:
                        continue

                    self.flat_lookup_proxies[dst_field] = item, src_field

    def register_subitem(self, parent, child):
        """
        Registers a registry item in a hierarchical relationship.
        """
        from nodewatcher.core.registry import fields as registry_fields

        # Verify parent registration
        if parent not in self.item_classes:
            raise ImproperlyConfigured("Parent class '{0}' is not yet registered!".format(parent._meta.object_name))

        top_level = True

        # TODO perform validation for multiple defined intra registry foreign keys

        # Augment the item with hierarchy information, discover foreign keys
        for field in child._meta.fields:
            if isinstance(field, registry_fields.IntraRegistryForeignKey) and issubclass(parent, field.rel.to):
                if not field.null:
                    # Foreign key is required for this subitem, so it can't be a top-level item
                    top_level = False

                # We have to use __dict__.get instead of getattr to prevent propagation of attribute access
                # to parent classes where these subitems might not be registered
                parent._registry_object_children = self._register_item_to_container(child,
                  parent.__dict__.get('_registry_object_children', django_datastructures.SortedDict()))

                # Setup the parent relation and verify that one doesn't already exist
                existing_parent = child.__dict__.get('_registry_object_parent', None)
                if existing_parent is not None and existing_parent.top_model() != parent.top_model():
                    raise ImproperlyConfigured("Registry item cannot have two object parents without a "
                      "common ancestor!")
                child._registry_object_parent = parent
                child._registry_object_parent_link = field

                parent._registry_has_children = True
                break
        else:
            raise ImproperlyConfigured("Missing IntraRegistryForeignKey linkage for parent-child relationship!")

        # Register item with the registry
        self._register_item(child, top_level)

    def _unregister_item(self, item_cls):
        """
        A helper method for unregistering a single item.

        :param item_cls: Registry item class
        """
        parent = item_cls.__base__
        if getattr(item_cls.RegistryMeta, 'hides_parent', False) and parent != self.item_base:
            parent._registry_hide_requests -= 1

        item_cls._registry_endpoint = None
        self.item_classes.remove(item_cls)

    def unregister_item(self, item_cls):
        """
        Unregisters a previously registered item or subitem. If the specified item
        defines the top-level schema item, all child items of this type will be unregistered.

        :param item_cls: Registry item class
        """
        if not issubclass(item_cls, self.item_base):
            raise TypeError("Specified class is not a valid registry item!")

        if item_cls not in self.item_classes:
            raise ValueError("Registry item '{0}' is not registered!".format(item_cls._meta.object_name))

        registry_id = item_cls.RegistryMeta.registry_id
        # TODO properly handle removal with new item list

        if item_cls.__base__ == self.item_base:
            # Top-level item, remove all registered subitems as well
            for item in self.item_object_toplevel[registry_id].values():
                self._unregister_item(item)

            del self.item_object_toplevel[registry_id]
            del self.item_registry[registry_id]
        else:
            # Item that subclasses a top-level item
            del self.item_object_toplevel[registry_id][item_cls._meta.module_name]
            assert len(self.item_object_toplevel[registry_id]) > 0
            self._unregister_item(item_cls)

    def get_children(self, parent = None):
        """
        Returns the child registry item classes that are available under the given
        parent registry item (via internal foreign key relationships). If None is
        specified as `parent` then only registry items that are available at the
        topmost level are returned.

        :param parent: Parent registry item class or None
        """
        if parent is None:
            return self.item_object_toplevel.values()
        else:
            return parent._registry_object_children.values()

    def get_top_level_queryset(self, root, registry_id):
        """
        Returns the queryset for fetching top-level items for the specific registry
        identifier.

        :param root: Instance of root class
        :param registry_id: A valid registry identifier
        :return: A tuple (queryset, top_class)
        """
        assert isinstance(root, self.model)
        top_level = self.item_registry[registry_id]
        return getattr(root, "{0}_{1}_{2}".format(self.namespace, top_level._meta.app_label, top_level._meta.module_name)), top_level

    def get_top_level_class(self, registry_id):
        """
        Returns a top-level registry item class for a specific identifier.

        :param registry_id: A valid registry identifier
        """
        try:
            return self.item_registry[registry_id]
        except KeyError:
            raise registry_access.UnknownRegistryIdentifier

    def get_accessor(self, root):
        """
        Returns the registry accessor for the specified root.
        """
        assert isinstance(root, self.model)
        return getattr(root, self.namespace)

    def get_registered_choices(self, choices_id):
        """
        Returns a list of previously registered choices.
        """
        return self.choices_registry.setdefault(choices_id, LazyChoiceList())

    def register_choice(self, choices_id, enum, text, limited_to = None):
        """
        Registers a new choice/enumeration.
        """
        self.get_registered_choices(choices_id).add_choice((enum, text), limited_to)

    def config_items(self):
        """
        A generator that iterates through registered items.
        """
        return iter(self.item_classes)

    def add_mixins(self, *mixins):
        """
        Adds one or more mixins to the top-level registry item that is associated
        with this registration point.

        :parma mixins: Mixin classes
        """
        self.item_base.__bases__ += tuple(mixins)

def create_point(model, namespace, mixins = None):
    """
    Creates a new registration point (= registry root).

    :param model: Root model
    :param namespace: Registration point namespace
    :param mixins: Optional list of mixin classes for the top-level registry item
    """
    # Properly handle deferred root model names
    try:
        app_label, model_name = model.split(".")
    except ValueError:
        raise ValueError("Deferred root model names must be of the form app_label.model_name!")
    except AttributeError:
        app_label = model._meta.app_label
        model_name = model._meta.object_name

    point_id = "%s.%s" % (model_name.lower(), namespace)
    if point_id not in registry_state.points:
        point = RegistrationPoint(model, namespace, point_id)
        registry_state.points[point_id] = point

        # Create a new top-level class
        class Meta(registry_models.RegistryItemBase.Meta):
            abstract = True

        if mixins is None:
            mixins = []

        base_name = "{0}{1}RegistryItem".format(model_name, namespace.capitalize())
        item_base = type(
          base_name,
          (registry_models.RegistryItemBase,) + tuple(mixins),
          {
            '__module__' : 'nodewatcher.core.registry.models',
            'Meta' : Meta,
            'root' : models.ForeignKey(
              model, null = False, editable = False, related_name = '{0}_%(app_label)s_%(class)s'.format(namespace)
            )
          }
        )
        point.item_base = item_base
        setattr(bases, base_name, item_base)

        def augment_root_model(model):
            # Augment the model with a custom manager and a custom accessor
            model.add_to_class(namespace, registry_access.RegistryAccessor(point))
            if not isinstance(model.objects, registry_lookup.RegistryLookupManager):
                del model.objects
                model.add_to_class('objects', registry_lookup.RegistryLookupManager(point))
                model._default_manager = model.objects

            # Update the model attribute in regpoint instance
            point.model = model

        # Try to load the model; if it is already loaded this will work, but if
        # not, we will need to defer part of object creation
        model = models.get_model(app_label, model_name, seed_cache = False, only_installed = False)
        if model:
            augment_root_model(model)
        else:
            registry_state.deferred_roots.setdefault((app_label, model_name), []).append(augment_root_model)

def handle_deferred_root(sender, **kwargs):
    """
    Finalizes any deferred root registrations.
    """
    key = (sender._meta.app_label, sender._meta.object_name)
    if key in registry_state.deferred_roots:
        for callback in registry_state.deferred_roots.pop(key, []):
            callback(sender)

models.signals.class_prepared.connect(handle_deferred_root)

def point(name):
    """
    Returns an existing registration point.

    :param name: Registration point name
    """
    return registry_state.points[name]

def register_form_for_item(item, form_class):
    """
    Registers a form for use with the specified registry item.

    :param item: Registry item class
    :param form_class: Form class
    """
    if not hasattr(item, '_forms'):
        item._forms = {}

    item._forms[item] = form_class
