from django.db import models

from web.core.allocation import pool as pool_models
from web.registry import fields as registry_fields
from web.registry import registration

class AddressAllocator(models.Model):
  """
  An abstract class defining an API for address allocator items.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#family")
  pool = registry_fields.ModelSelectorKeyField(pool_models.Pool, limit_choices_to = { 'parent' : None })
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
    except pool_models.Pool.DoesNotExist:
      self.fields['cidr'] = registry_fields.SelectorFormField(label = "CIDR")

@registration.register_validation_hook("node.config")
def node_address_allocation(node):
  """
  Handles address allocation for a node acoording to requests and registered
  allocators.
  """
  # Automatically discover currently available allocation sources
  allocation_sources = [
    item
    for item in registration.point("node.config").config_items()
    if issubclass(item, AddressAllocator)
  ]
  
  # Create requests from allocation sources
  requests = set()
  for src in allocation_sources:
    for request in node.config.by_path(src.RegistryMeta.registry_id):
      if isinstance(request, src):
        requests.add(request)
  
  print requests
  # TODO Compare requests with existing allocations and do something about it

