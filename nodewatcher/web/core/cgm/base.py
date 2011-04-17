from registry import registration

# Registered platform modules
PLATFORM_REGISTRY = {}

class ValidationError(Exception):
  pass

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
  
  def generate(self, node):
    """
    Generates a concrete configuration for this platform.
    """
    cfg = self.config_class()
    
    # Execute the module chain in order
    for _, module in sorted(self._modules):
      module(node, cfg)
    
    return cfg
  
  def format(self, cfg):
    raise NotImplementedError

  def build(self):
    raise NotImplementedError
  
  def defer_format_build(self, node, cfg):
    # TODO Defer formatting and build process via Celery
    
    # TODO Don't forget to add proper Celery routing so this doesn't
    #      get routed to the workers for generating graphs!
    pass
  
  def register_module(self, order, module):
    """
    Registers a new platform module.
    
    @param order: Call order
    @param module: Module implementation function
    """
    self._modules.append((order, module))

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
  
  # Register the choice in configuration registry
  registration.register_choice("core.general#platform", enum, text)

def get_platform(platform):
  """
  Returns the given platform implementation.
  """
  try:
    return PLATFORM_REGISTRY[platform]
  except KeyError:
    raise KeyError, "Platform '{0}' does not exist!".format(platform)

def register_platform_module(platform, order):
  """
  Registers a new platform module.
  """
  def wrapper(f):
    get_platform(platform).register_module(order, f)
    return f
  
  return wrapper

