from nodewatcher.modules.monitor.topology import base
from nodewatcher.modules.monitor.topology.pool import pool

pool.register(base.NodeAttribute('l', 'core.location#geolocation', transform=lambda loc: loc.coords))
