import copy

from django.core.exceptions import ImproperlyConfigured

from registry import registration

class RouterPort(object):
  """
  An abstract descriptor of a router port.
  """
  def __init__(self, identifier, description):
    """
    Class constructor.
    """
    self.identifier = identifier
    self.description = description

class EthernetPort(RouterPort):
  """
  Describes a router's ethernet port.
  """
  pass

class RouterRadio(object):
  """
  An abstract descriptor of a router radio.
  """
  def __init__(self, identifier, description):
    """
    Class constructor.
    """
    self.identifier = identifier
    self.description = description

class IntegratedRadio(RouterRadio):
  """
  Describes a router's integrated radio.
  """
  pass

class MiniPCIRadio(RouterRadio):
  """
  Describes a router's MiniPCI slot for a radio.
  """
  pass

# A list of attributes that are required to be defined
REQUIRED_ROUTER_ATTRIBUTES = set([
  'identifier',
  'name',
  'architecture',
  'radios',
  'ports',
])

class RouterModelMeta(type):
  """
  Type for router models.
  """
  def __new__(cls, name, bases, attrs):
    """
    Creates a new RouterModelBase class.
    """
    if name != 'RouterModelBase':
      # Validate the presence of all attributes
      required_attrs = copy.deepcopy(REQUIRED_ROUTER_ATTRIBUTES)
      for attr in attrs:
        if attr.startswith('_'):
          continue
        if attr not in required_attrs:
          raise ImproperlyConfigured("Attribute '{0}' is not a valid router model attribute!".format(attr))
        
        required_attrs.remove(attr)
      
      if len(required_attrs) > 0:
        raise ImproperlyConfigured("The following attributes are required for router model specification: {0}!".format(
          ", ".join(required_attrs)
        ))
      
      # Router ports and radios cannot both be empty
      if not len(attrs['radios']) and not len(attrs['ports']):
        raise ImproperlyConfigured("A router cannot be without radios and ports!")
      
      # Validate that list of ports only contains RouterPort instances
      if len([x for x in attrs['ports'] if not isinstance(x, RouterPort)]):
        raise ImproperlyConfigured("List of router ports may only contain RouterPort instances!")
      
      # Validate that list of radios only contains RouterRadio instances
      if len([x for x in attrs['radios'] if not isinstance(x, RouterRadio)]):
        raise ImproperlyConfigured("List of router radios may only contain RouterRadio instances!")
    
    return type.__new__(cls, name, bases, attrs)

class RouterModelBase(object):
  """
  An abstract router hardware descriptor.
  """
  __metaclass__ = RouterModelMeta
  
  @classmethod
  def register(cls, platform):
    """
    Performs router model registration.
    """
    # Register a new choice in the configuration registry
    registration.point("node.config").register_choice("core.general#model", cls.identifier, cls.name,
      limited_to = ("core.general#platform", platform.name)
    )
    
    # Register a new choice for available router ports
    for port in cls.ports:
      registration.point("node.config").register_choice("core.interfaces#eth_port", port.identifier, port.description,
        limited_to = ("core.general#model", cls.identifier)
      )
    
    # Register a new choice for available router radios
    for radio in cls.radios:
      registration.point("node.config").register_choice("core.interfaces#wifi_radio", radio.identifier, radio.description,
        limited_to = ("core.general#model", cls.identifier)
      )
  
  def __init__(self):
    """
    Prevent instantiation of this class.
    """
    raise TypeError("Router model descriptors are non-instantiable!")
  
  def __setattr__(self, key, value):
    """
    Prevent modification of router model descriptors.
    """
    raise AttributeError("Router model descriptors are immutable!")

