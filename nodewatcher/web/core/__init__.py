from web.registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Additional imports that require the points to be registered
from web.core import allocation as core_allocation

# Dependencies
import web.nodes

@registration.register_validation_hook("node.config")
def node_address_allocation(node):
  """
  Handles address allocation for a node acoording to requests and registered
  allocators.
  """
  from django.db import models
  from django.contrib.contenttypes.models import ContentType
  from web.core.allocation import pool as pool_models
  
  # Automatically discover currently available allocation sources
  allocation_sources = [
    item
    for item in registration.point("node.config").config_items()
    if issubclass(item, core_allocation.AddressAllocator)
  ]
  
  # Automatically discover available allocation pool implementations
  allocation_pools = [
    item
    for item in models.get_models()
    if issubclass(item, pool_models.PoolBase)
  ]
  
  # Create requests from allocation sources
  allocations = set()
  for pool_cls in allocation_pools:
    allocations.update(
      pool_cls.objects.filter(
        alloc_content_type__pk = ContentType.objects.get_for_model(node).id,
        alloc_object_id = node.pk
      )
    )
  
  for src in allocation_sources:
    for request in node.config.by_path(src.RegistryMeta.registry_id):
      if isinstance(request, src):
        for allocation in allocations.copy():
          if request.is_satisfied_by(allocation):
            allocations.remove(allocation)
            break
        else:
          # Need to allocate additional resources
          request.satisfy(node)
  
  # Free existing unused resources
  # TODO Do this only when saving for real, not on validation runs
  for unused in allocations:
    unused.free()

