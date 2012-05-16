from web.core import allocation as core_allocation
from web.core import models as core_models
from web.core.allocation import pool as pool_models
from web.registry import registration
from web.registry.forms import processors

class AutoPoolAllocator(processors.RegistryFormProcessor):
  """
  A form processor that attempts to automatically satisfy allocation
  requests defined by AddressAllocator config items.
  """
  def __init__(self):
    """
    Class constructor.
    """
    self.allocations = set()

  def preprocess(self, node):
    """
    Performs preprocessing of allocations for `node`.
    """
    if node is None:
      # A new node is being registered, so we have nothing to add here
      return

    # Automatically discover currently available allocation sources
    allocation_sources = [
      item
      for item in registration.point("node.config").config_items()
      if issubclass(item, core_allocation.AddressAllocator)
    ]

    for src in allocation_sources:
      for allocation in node.config.by_path(src.RegistryMeta.registry_id):
        if isinstance(allocation, src):
          self.allocations.add(allocation)

  def postprocess(self, node):
    """
    Automatically satisfy allocation requests for `node`.
    """
    # Automatically discover currently available allocation sources
    allocation_sources = [
      item
      for item in registration.point("node.config").config_items()
      if issubclass(item, core_allocation.AddressAllocator)
    ]

    routerid_requests = {}
    unsatisfied_requests = []
    for src in allocation_sources:
      for request in node.config.by_path(src.RegistryMeta.registry_id):
        if isinstance(request, src):
          # Use the request/allocation with lowest identifier as a source for
          # node's router identifier (per family)
          family = request.get_routerid_family()
          if family in routerid_requests:
            if request.pk < routerid_requests[family].pk:
              routerid_requests[family] = request
          else:
            routerid_requests[family] = request

          if not request.is_satisfied():
            unsatisfied_requests.append(request)
          else:
            for allocation in self.allocations.copy():
              if allocation.exactly_matches(request):
                self.allocations.remove(allocation)
                break

    # Attempt to reuse existing resources before requesting new ones
    for request in unsatisfied_requests:
      for unused in self.allocations.copy():
        if request.satisfy_from(unused):
          self.allocations.remove(unused)
          break
      else:
        request.free()
        request.satisfy(node)

        # Prevent the allocation from being freed
        if request in self.allocations:
          self.allocations.remove(request)

    # Free existing unused resources
    # TODO Do this only when saving for real, not on validation runs
    for unused in self.allocations:
      unused.free()

    # Recompute router identifiers
    # TODO Do this only when saving for real, not on validation runs
    for family, request in routerid_requests.iteritems():
      try:
        rid = node.config.core.routerid(queryset = True).get(family = family)
      except core_models.RouterIdConfig.DoesNotExist:
        rid = node.config.core.routerid(create = core_models.RouterIdConfig)

      rid.router_id = request.get_routerid()
      rid.save()
