from nodewatcher.modules.monitor.topology import base
from nodewatcher.modules.monitor.topology.pool import pool

pool.register(base.NodeAttribute('l', 'core.location__geolocation', transform=lambda loc: loc.coords))
