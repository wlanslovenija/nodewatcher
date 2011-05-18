import collections

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import datastructures as django_datastructures

from registry import state as registry_state
from registry import models as registry_models
from registry import lookup as registry_lookup
from registry import access as registry_access
from web.utils import datastructures as nw_datastructures

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
  """
  def __init__(self, model, namespace, point_id):
    """
    Class constructor.
    """
    self.model = model
    self.namespace = namespace
    self.name = point_id
    self.item_registry = {}
    self.item_list = django_datastructures.SortedDict()
    self.item_classes = {}
    self.choices_registry = {}
    self.flat_lookup_proxies = {}
    self.validation_hooks = []
  
  def _register_item(self, item):
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
      self.item_classes[item] = True
    
    # Insert into item list
    items = self.item_list
    item_dict = items.setdefault(
      (getattr(item.RegistryMeta, 'form_order', 0), item.RegistryMeta.registry_id),
      {}
    )
    item_dict[item._meta.module_name] = item
    self.item_list = django_datastructures.SortedDict(sorted(items.items(), key = lambda x: x[0]))
    
    # Only record the top-level item in the registry as there could be multiple
    # specializations that define their own limits
    if item.__base__ == self.item_base:
      registry_id = item.RegistryMeta.registry_id
      if registry_id in self.item_registry:
        raise ImproperlyConfigured(
          "Multiple top-level registry items claim identifier '{0}'! Claimed by '{1}' and '{2}'.".format(
            registry_id, self.item_registry[registry_id]._meta.object_name, item._meta.object_name
        ))
      
      self.item_registry[registry_id] = item
    
    # Include registration point in item class
    item._registry_regpoint = self
    
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
    from registry import fields as registry_fields
    
    # Verify parent registration
    if parent not in self.item_classes:
      raise ImproperlyConfigured("Parent class '{0}' is not yet registered!".format(parent._meta.object_name))
    
    self._register_item(child)
    
    # Augment the item with hierarchy information, discover foreign keys
    for field in child._meta.fields:
      if isinstance(field, registry_fields.IntraRegistryForeignKey) and issubclass(parent, field.rel.to):
        parent._registry_has_children = True
        parent._registry_allowed_children = parent.__dict__.get('_registry_allowed_children', set())
        parent._registry_allowed_children.add(child)
        
        if hasattr(child, '_registry_parents'):
          child._registry_parents[parent] = field
        else:
          child._registry_parents = { parent : field }
        
        break
    else:
      raise ImproperlyConfigured("Missing IntraRegistryForeignKey linkage for parent-child relationship!")
  
  def get_top_level_queryset(self, root, registry_id):
    """
    Returns the queryset for fetching top-level items for the specific registry
    identifier.
    
    @param root: Instance of root class
    @param registry_id: A valid registry identifier
    @return: A tuple (queryset, top_class)
    """
    assert isinstance(root, self.model)
    top_level = self.item_registry[registry_id]
    return getattr(root, "{0}_{1}_{2}".format(self.namespace, top_level._meta.app_label, top_level._meta.module_name)), top_level
  
  def get_top_level_class(self, registry_id):
    """
    Returns a top-level registry item class for a specific identifier.
    
    @param registry_id: A valid registry identifier
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

def create_point(model, namespace):
  """
  Creates a new registration point (= registry root).
  
  @param model: Root model
  @param namespace: Registration point namespace
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
    
    base_name = "{0}{1}RegistryItem".format(model_name, namespace.capitalize())
    item_base = type(
      base_name,
      (registry_models.RegistryItemBase,),
      {
        '__module__' : 'registry.models',
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
    
    # Try to load the model; if it is already loaded this will work, but if
    # not, we will need to defer part of object creation
    model = models.get_model(app_label, model_name, False)
    if model:
      augment_root_model(model)
    else:
      registry_state.deferred_roots[app_label, model_name] = augment_root_model

def handle_deferred_root(sender, **kwargs):
  """
  Finalizes any deferred root registrations.
  """
  key = (sender._meta.app_label, sender._meta.object_name)
  if key in registry_state.deferred_roots:
    registry_state.deferred_roots.pop(key, lambda x: None)(sender)

models.signals.class_prepared.connect(handle_deferred_root)

def point(name):
  """
  Returns an existing registration point.
  
  @param name: Registration point name
  """
  return registry_state.points[name]

def register_form_for_item(item, form_class):
  """
  Registers a form for use with the specified registry item.
  
  @param item: Registry item class
  @param form_class: Form class
  """
  if not hasattr(item, '_forms'):
    item._forms = {}
  
  item._forms[item] = form_class

def register_validation_hook(regpoint):
  """
  A decorator that registers a new validation hook that gets applied after
  form validation for this registration point is completed.
  """
  def wrapper(f):
    point(regpoint).validation_hooks.append(f)
    return f
  
  return wrapper

