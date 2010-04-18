class InvalidPluginClass(Exception):
  """
  This exception gets raised when the plugin class does not inherit
  from a predefined superclass.
  """
  pass

def load_plugin(module_path, required_super = None):
  """
  A helper function to load a plugin (class) given its full path
  as a string. Paths are valid Python module names that must be
  importable at time of calling this method.
  
  @param module_path: A valid module path that ends in a class name
  @param required_super: Optional required superclass
  @return: The given class
  """
  module = module_path[0:module_path.rfind('.')]
  className = module_path[module_path.rfind('.') + 1:]
  m = __import__(module, globals(), locals(), [className], -1)
  cls = m.__dict__[className]
  
  if required_super is not None and not issubclass(cls, required_super):
    raise InvalidPluginClass
  
  return cls

