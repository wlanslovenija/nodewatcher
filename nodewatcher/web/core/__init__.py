from registry import registration

# Create registration points
registration.create_point("nodes.Node", "config")
registration.create_point("nodes.Node", "monitoring")

# Address allocation
import core.allocation

# Dependencies
import nodes
