from django.contrib.contenttypes.models import ContentType

class UnknownRegistryIdentifier(Exception):
  pass

class UnknownRegistryClass(Exception):
  pass

class RegistryResolver(object):
  """
  Resolves registry identifiers in a hierarchical manner.
  """
  def __init__(self, regpoint, root, path = None):
    """
    Class constructor.
    
    @param regpoint: Registration point
    @param root: Root model instance
    @param path: Current path in the hierarhcy
    """
    self._regpoint = regpoint
    self._root = root
    self._path = path
  
  def to_partial(self):
    """
    Formats the root's registry hierarchy to partial config format.
    """
    partial = {}
    for path, _ in self._regpoint.item_registry.iteritems():
      partial[path] = [x.cast() for x in self.by_path(path, queryset = True)]
    
    return partial
  
  def by_path(self, path, create = None, queryset = False, onlyclass = None):
    """
    Resolves the registry hierarchy.
    """
    if path in self._regpoint.item_registry:
      # Determine which class the root is using for configuration
      cfg, top_level = self._regpoint.get_top_level_queryset(self._root, path)
      if onlyclass is not None:
        cfg = cfg.filter(content_type = ContentType.objects.get_for_model(onlyclass))
      if queryset:
        return cfg.all()
      
      if getattr(top_level.RegistryMeta, 'multiple', False):
        # Model supports multiple configuration options of this type
        if create is not None:
          if not issubclass(create, top_level):
            raise TypeError, "Not a valid registry item class for '{0}'!".format(path)
          
          return create(root = self._root)
        else:
          return map(lambda x: x.cast(), cfg.all())
      else:
        # Only a single configuration option is supported
        try:
          return cfg.all()[0].cast()
        except (IndexError, top_level.DoesNotExist):
          if create is not None:
            if not issubclass(create, top_level):
              raise TypeError, "Not a valid registry item class for '{0}'!".format(path)
            
            return create(root = self._root)
          else:
            return None
    else:
      raise UnknownRegistryIdentifier

  def __iter__(self):
    """
    Returns an iterator over all registry items that are present under
    this registration point.
    """
    for obj in self._root._meta.get_all_related_objects():
      if issubclass(obj.model, self._regpoint.item_base):
        for model in getattr(self._root, obj.field.rel.related_name).all():
          yield model

  def __getattr__(self, key):
    """
    Constructs hierarchical names by simulating attribute access.
    """
    key = key if self._path is None else "{0}.{1}".format(self._path, key)
    return RegistryResolver(self._regpoint, self._root, key)
  
  def __call__(self, **kwargs):
    """
    Resolves the registry hierarchy.
    """
    return self.by_path(self._path, **kwargs)

class RegistryAccessor(object):
  """
  A convenience class for accessing the registry via root models.
  """
  def __init__(self, regpoint):
    self.regpoint = regpoint
  
  def __get__(self, instance, owner):
    return RegistryResolver(self.regpoint, instance)

# Cache for class resolutions
CTYPE_CACHE = {}

def get_model_class_by_name(name):
  """
  Returns the model class identified by its name.
  
  @param name: Model class name
  """
  name = name.lower()
  try:
    ctype = CTYPE_CACHE[name]
  except KeyError:
    try:
      ctype = ContentType.objects.get(model = name).model_class()
    except ContentType.DoesNotExist:
      raise UnknownRegistryClass
    
    CTYPE_CACHE[name] = ctype
  
  return ctype

