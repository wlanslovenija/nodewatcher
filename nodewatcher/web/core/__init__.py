from web.registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Additional imports that require the points to be registered
from web.core import allocation as core_allocation

# Dependencies
import web.nodes

@registration.register_validation_hook("node.config", order = "pre", result_id = "allocations")
def node_address_allocation_setup(node):
  """
  Handles address allocation for a node acoording to requests and registered
  allocators.
  """
  allocations = set()
  
  # Automatically discover currently available allocation sources
  allocation_sources = [
    item
    for item in registration.point("node.config").config_items()
    if issubclass(item, core_allocation.AddressAllocator)
  ]
  
  for src in allocation_sources:
    for allocation in node.config.by_path(src.RegistryMeta.registry_id):
      if isinstance(allocation, src):
        allocations.add(allocation)
  
  return allocations

@registration.register_validation_hook("node.config", order = "post", result_id = "allocations")
def node_address_allocation(node, allocations):
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
  
  unsatisfied_requests = []
  for src in allocation_sources:
    for request in node.config.by_path(src.RegistryMeta.registry_id):
      if isinstance(request, src):
        if not request.is_satisfied():
          unsatisfied_requests.append(request)
        else:
          for allocation in allocations.copy():
            if allocation.exactly_matches(request):
              allocations.remove(allocation)
              break
  
  # Attempt to reuse existing resources before requesting new ones
  for request in unsatisfied_requests:
    for unused in allocations.copy():
      if request.satisfy_from(unused):
        allocations.remove(unused)
        break
    else:
      request.free()
      request.satisfy(node)
  
  # Free existing unused resources
  # TODO Do this only when saving for real, not on validation runs
  for unused in allocations:
    unused.free()

