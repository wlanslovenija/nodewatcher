from django.db import models

# TODO pools should be moved from nodes app to core app
from nodes import models as nodes_models
from registry import fields as registry_fields
from registry import registration

class AddressAllocator(models.Model):
  """
  An abstract class defining an API for address allocator items.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#family")
  # TODO pools should be moved from nodes app to core app
  pool = registry_fields.ModelSelectorKeyField(nodes_models.Pool, limit_choices_to = { 'parent' : None })
  cidr = models.IntegerField(default = 27)
  usage = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#usage")
  
  class Meta:
    abstract = True

class AddressAllocatorFormMixin(object):
  """
  A mixin for address allocator forms.
  """
  def modify_to_context(self, item, cfg):
    """
    Dynamically modifies the form.
    """
    # Only display pools that are available to the selected project
    qs = self.fields['pool'].queryset
    qs = qs.filter(projects = cfg['core.general'][0].project)
    # TODO pools should use registered family identifiers
    qs = qs.filter(family = 4 if item.family == "ipv4" else 6)
    self.fields['pool'].queryset = qs
    
    # Only display CIDR range that is available for the selected pool
    try:
      pool = item.pool
      self.fields['cidr'] = registry_fields.SelectorFormField(
        label = "CIDR",
        choices = [(plen, "/%s" % plen) for plen in xrange(pool.min_prefix_len, pool.max_prefix_len + 1)],
        initial = pool.default_prefix_len,
        coerce = int,
        empty_value = None
      )
    except nodes_models.Pool.DoesNotExist:
      self.fields['cidr'] = registry_fields.SelectorFormField(label = "CIDR")

allocation_sources = set()

def register_allocation_source(regitem):
  """
  Registers a new address allocation request source.
  
  @param regitem: Registry item class
  """
  if not issubclass(regitem, registration.bases.NodeConfigRegistryItem):
    raise TypeError("Allocation sources must be node configuration registry items!")
  
  if not issubclass(regitem, AddressAllocator):
    raise TypeError("Allocation sources must implement AddressAllocator API!")
  
  allocation_sources.add(regitem)

def unregister_allocation_source(regitem):
  """
  Removes an existing new address allocation request source.
  
  @param regitem: Registry item class
  """
  allocation_sources.remove(regitem)

@registration.register_validation_hook("node.config")
def node_address_allocation(node):
  """
  Handles address allocation for a node acoording to requests and registered
  allocators.
  """
  requests = set()
  for src in allocation_sources:
    for request in node.config.by_path(src.RegistryMeta.registry_id):
      if isinstance(request, src):
        requests.add(request)
  
  # TODO Compare requests with existing allocations and do something about it

