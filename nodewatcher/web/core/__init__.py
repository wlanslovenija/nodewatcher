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
  # Automatically discover currently available allocation sources
  allocation_sources = [
    item
    for item in registration.point("node.config").config_items()
    if issubclass(item, core_allocation.AddressAllocator)
  ]
  
  # Create requests from allocation sources
  allocations = set(node.allocations.all())
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

