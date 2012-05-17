from nodewatcher.registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Additional imports that require the points to be registered
from nodewatcher.core import allocation as core_allocation

# Dependencies
import nodewatcher.nodes
