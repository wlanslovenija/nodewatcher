import collections

from django.db import models
from django.utils import datastructures

from registry import state as registry_state
from registry import models as registry_models
from registry import lookup as registry_lookup
from registry import access as registry_access 

bases = registry_state.bases

class LazyChoiceList(collections.Sequence):
  def __init__(self):
    super(LazyChoiceList, self).__init__()
    self._list = []
  
  def __len__(self):
    return len(self._list)

  def __getitem__(self, index):
    return self._list[index]
  
  def __nonzero__(self):
    return True

class RegistrationPoint(object):
  """
  Registration point is a state holder for registry operations. There can be
  multiple registration points, each rooted at its own model.
  """
  def __init__(self, model, namespace):
    """
    Class constructor.
    """
    self.model = model
    self.namespace = namespace
    self.item_registry = {}
    self.item_list = datastructures.SortedDict()
    self.choices_registry = {}
    self.flat_lookup_proxies = {}
  
  def register_item(self, item):
    """
    Registers a new item to this registration point.
    """
    if not issubclass(item, self.item_base):
      raise TypeError("Not a valid registry item class!")
    
    # Sanity check for object names
    if '_' in item._meta.object_name:
      raise ImproperlyConfigured("Registry items must not have underscores in class names!")
    
    # Insert into item list
    items = self.item_list
    item_dict = items.setdefault(
      (getattr(item.RegistryMeta, 'form_order', 0), item.RegistryMeta.registry_id),
      {}
    )
    item_dict[item._meta.module_name] = item
    self.item_list = datastructures.SortedDict(sorted(items.items(), key = lambda x: x[0]))
    
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
    
    # Include registration point in item class
    item._registry_regpoint = self
  
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
      raise UnknownRegistryIdentifier
  
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
  
  def register_choice(self, choices_id, enum, text):
    """
    Registers a new choice/enumeration.
    """
    choices = self.choices_registry.setdefault(choices_id, LazyChoiceList())._list
    if any([x == enum for x, _ in choices]):
      return
    
    choices.append((enum, text))

def create_point(model, namespace):
  """
  Creates a new registration point (= registry root).
  
  @param model: Root model
  @param namespace: Registration point namespace
  """
  point_id = "%s.%s" % (model._meta.module_name, namespace)
  if point_id not in registry_state.points:
    point = RegistrationPoint(model, namespace)
    registry_state.points[point_id] = point
    
    # Augment the model with a custom manager and a custom accessor
    model.add_to_class("%s_objects" % namespace, registry_lookup.RegistryLookupManager(point))
    model.add_to_class(namespace, registry_access.RegistryAccessor(point))
    
    # Create a new top-level class
    class Meta(registry_models.RegistryItemBase.Meta):
      abstract = True
    
    base_name = "{0}{1}RegistryItem".format(model._meta.object_name, namespace.capitalize())
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

