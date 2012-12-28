from nodewatcher.registry import registration

# Create registration point
registration.create_point("nodes.Node", "config")

# Additional imports that require the point to be registered
from nodewatcher.core import allocation as core_allocation

# Dependencies
import nodewatcher.legacy.nodes
