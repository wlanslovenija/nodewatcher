from web.registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Additional imports that require the points to be registered
from web.core import allocation as core_allocation

# Dependencies
import web.nodes
