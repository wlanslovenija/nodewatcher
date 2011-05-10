from registry import registration

# Registered platform modules
PLATFORM_REGISTRY = {}

class ValidationError(Exception):
  pass

class RouterModel(object):
  """
  A class that contains router model metadata.
  """
  FIELDS = (
    'name',
    'architecture',
    'supported_radios',
  )
  
  def __init__(self, **kwargs):
    """
    Class constructor.
    """
    required = set(self.FIELDS)
    for key, value in kwargs.iteritems():
      setattr(self, key, value)
      required.remove(key)
    
    if len(required):
      raise AttributeError("The following fields are required: {0}".format(",".join(required)))
  
  def __setattr__(self, key, value):
    """
    Only allow setting already defined attributes.
    """
    if key not in self.FIELDS:
      raise AttributeError("Field '{0}' is not a valid router model attribute!".format(key))
    
    object.__setattr__(self, key, value)

class PlatformConfiguration(object):
  """
  A flexible in-memory platform configuration store that is used
  by modules to make modifications and perform configuration. The
  default implementation is empty as this is platform-specific.
  """
  pass

class PlatformBase(object):
  """
  An abstract base class for all platform implementations.
  """
  config_class = PlatformConfiguration
  
  def __init__(self):
    """
    Class constructor.
    """
    self._modules = []
    self._packages = []
    self._router_models = {}
  
  def generate(self, node):
    """
    Generates a concrete configuration for this platform.
    """
    cfg = self.config_class()
    
    # Execute the module chain in order
    for _, module, router_model in sorted(self._modules):
      if router_model is None or router_model == node.config.core.general().model:
        module(node, cfg)
    
    # Process packages
    for name, cfgclass, package in self._packages:
      package(node, node.config.core.packages(onlyclass = cfgclass), cfg)
      self.install_optional_package(name)
    
    return cfg
  
  def format(self, cfg):
    raise NotImplementedError

  def build(self):
    raise NotImplementedError
  
  def install_optional_package(self, name):
    raise NotImplementedError
  
  def defer_format_build(self, node, cfg):
    # TODO Defer formatting and build process via Celery
    
    # TODO Don't forget to add proper Celery routing so this doesn't
    #      get routed to the workers for generating graphs!
    pass
  
  def register_module(self, order, module, router_model = None):
    """
    Registers a new platform module.
    
    @param order: Call order
    @param module: Module implementation function
    @param router_model: Optional router model
    """
    if [x for x in self._modules if x[1] == module]:
      return
    
    self._modules.append((order, module, router_model))
  
  def register_package(self, name, config, package):
    """
    Registers a new platform package.
    
    @param name: Platform-dependent package name
    @param config: Configuration class
    @param package: Package implementation function
    """
    if [x for x in self._packages if x[2] == package]:
      return
    
    self._packages.append((name, config, package))
  
  def register_router_model(self, model, **properties):
    """
    Registers a new router model.
    
    @param model: Unique model identifier
    """
    self._router_models[model] = RouterModel(**properties)
    
    # Register a new choice in the configuration registry
    registration.point("node.config").register_choice("core.general#model", model, properties['name'],
      limited_to = ("core.general#platform", self.platform_name)
    )
  
  def get_router_model(self, model):
    """
    Returns a router model descriptor.
    
    @param model: Unique model identifier
    """
    return self._router_models[model]

def register_platform(enum, text, platform):
  """
  Registers a new platform with the Configuration Generation Modules
  system.
  """
  if not isinstance(platform, PlatformBase):
    raise TypeError, "Platform formatter/builder implementation must be a PlatformBase instance!"
  
  if enum in PLATFORM_REGISTRY:
    raise ValueError, "Platform '{0}' is already registered!".format(enum)
  
  PLATFORM_REGISTRY[enum] = platform
  platform.platform_name = enum
  
  # Register the choice in configuration registry
  registration.point("node.config").register_choice("core.general#platform", enum, text)

def get_platform(platform):
  """
  Returns the given platform implementation.
  """
  try:
    return PLATFORM_REGISTRY[platform]
  except KeyError:
    raise KeyError, "Platform '{0}' does not exist!".format(platform)

def register_platform_module(platform, order, router_model = None):
  """
  Registers a new platform module.
  """
  def wrapper(f):
    get_platform(platform).register_module(order, f, router_model = router_model)
    return f
  
  return wrapper

def register_platform_package(platform, name, cfgclass):
  """
  Registers a new platform package.
  """
  def wrapper(f):
    get_platform(platform).register_package(name, cfgclass, f)
  
  return wrapper

def register_router_model(platform, model, **properties):
  """
  Registers a new router model.
  """
  get_platform(platform).register_router_model(model, **properties)

