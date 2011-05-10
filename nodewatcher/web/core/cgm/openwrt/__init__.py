from django.utils.translation import ugettext as _

from registry.cgm import base as cgm_base

class UCISection(object):
  """
  Represents a configuration section in UCI.
  """
  def __init__(self, typ = None):
    """
    Class constructor.
    """
    self.__dict__['_typ'] = typ
    self.__dict__['_values'] = {}
  
  def __setattr__(self, name, value):
    """
    Sets a configuration attribute.
    """
    self._values[name] = value
  
  def __delattr__(self, name):
    """
    Deletes a configuration attribute.
    """
    del self._values[name]
  
  def __getattr__(self, name):
    """
    Returns a configuration attribute's value.
    """
    return self._values[name]
  
  def format(self, root, section, idx = None):
    """
    Formats the configuration tree so it is suitable for loading into UCI.
    """
    output = []
    
    if self._typ is not None:
      # Named sections
      output.append("{0}.{1}={2}".format(root, section, self._typ))
      for key, value in self._values.iteritems():
        output.append("{0}.{1}.{2}={3}".format(root, section, key, value))
    else:
      # Ordered sections
      output.append("{0}.@{1}[{2}]={1}".format(root, section, idx))
      for key, value in self._values.iteritems():
        output.append("{0}.@{1}[{2}].{3}={4}".format(root, section, idx, key, value))
    
    return output

class UCIRoot(object):
  """
  Represents an UCI configuration file with multiple named and ordered
  sections.
  """
  def __init__(self, root):
    """
    Class constructor.
    
    @param root: Root name
    """
    self._root = root
    self._named_sections = {}
    self._ordered_sections = {}
  
  def add(self, *args, **kwargs):
    """
    Creates a new UCI section. An ordered section should be specified by using
    a single argument and a named section by using a single keyword argument.
    
    @return: The newly created UCISection
    """
    if len(args) > 1 or len(kwargs) > 1 or len(args) == len(kwargs):
      raise ValueError
    
    if kwargs:
      # Adding a named section
      section_key = kwargs.values()[0]
      section = UCISection(typ = kwargs.keys()[0])
      
      # Check for duplicates to avoid screwing up existing lists and sections
      if section_key in self._named_sections:
        raise ValueError, "UCI section '{0}' is already defined!".format(section_key)
      
      self._named_sections[section_key] = section
    else:
      # Adding an ordered section
      section = UCISection()
      self._ordered_sections.setdefault(args[0], []).append(section)
    
    return section
  
  def __getattr__(self, section):
    """
    Retrieves the wanted UCI section.
    """
    try:
      return self._named_sections[section]
    except KeyError:
      return self._ordered_sections[section]
  
  def format(self):
    """
    Formats the configuration tree so it is suitable for loading into UCI.
    """
    output = []
    for name, section in self._named_sections.iteritems():
      output += section.format(self._root, name)
    
    for name, sections in self._ordered_sections.iteritems():
      for idx, section in enumerate(sections):
        output += section.format(self._root, name, idx)
    
    return output

class UCIConfiguration(cgm_base.PlatformConfiguration):
  """
  An in-memory implementation of UCI configuration.
  """
  def __init__(self):
    """
    Class constructor.
    """
    self._roots = {}
  
  def __getattr__(self, root):
    """
    Returns the desired UCI root (config file).
    """
    return self._roots.setdefault(root, UCIRoot(root))
  
  def format(self):
    """
    Formats the configuration tree so it is suitable for loading into UCI.
    """
    output = []
    for name, root in self._roots.iteritems():
      output += root.format()
    
    return output

class PlatformOpenWRT(cgm_base.PlatformBase):
  """
  OpenWRT platform descriptor.
  """
  config_class = UCIConfiguration
  
  def format(self, cfg):
    raise NotImplementedError

  def build(self):
    raise NotImplementedError
  
  def install_optional_package(self, name):
    # TODO
    pass

cgm_base.register_platform("openwrt", _("OpenWRT"), PlatformOpenWRT())

# Load all modules for this platform that are included in the core
import core.cgm.openwrt.general
import core.cgm.openwrt.vpn

# Load all model-specific modules
import core.cgm.openwrt.fon2100

