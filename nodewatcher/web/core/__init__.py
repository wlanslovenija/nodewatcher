from web.registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Address allocation
import web.core.allocation

# Dependencies
import web.nodes
