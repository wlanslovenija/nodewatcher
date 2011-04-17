from registry import state as registry_state

class UnknownRegistryIdentifier(Exception):
  pass

class RegistryResolver(object):
  """
  Resolves registry identifiers in a hierarchical manner.
  """
  def __init__(self, node, path = None):
    """
    Class constructor.
    
    @param node: Node instance
    @param path: Current path in the hierarhcy
    """
    self._node = node
    self._path = path
  
  def __getattr__(self, key):
    """
    Constructs hierarchical names by simulating attribute access.
    """
    key = key if self._path is None else "{0}.{1}".format(self._path, key)
    return RegistryResolver(self._node, key)
  
  def __call__(self, create = None):
    """
    Resolves the registry hierarchy.
    """
    if self._path in registry_state.ITEM_REGISTRY:
      # Determine which class the node is using for configuration
      top_level = registry_state.ITEM_REGISTRY[self._path]
      cfg = getattr(self._node, "config_{0}_{1}".format(top_level._meta.app_label, top_level._meta.module_name))
      
      try:
        item = cfg.all()[0]
        if item.cls_id == top_level._meta.module_name:
          return item
        else:
          return getattr(item, item.cls_id)
      except (IndexError, top_level.DoesNotExist):
        if create is not None:
          if not issubclass(create, top_level):
            raise TypeError, "Not a valid registry item class for '{0}'!".format(self._path)
          
          return create(node = self._node)
        else:
          return None
    else:
      raise UnknownRegistryIdentifier

class Registry(object):
  """
  A convenience class for accessing the registry via Node models.
  """
  def __get__(self, instance, owner):
    return RegistryResolver(instance)

