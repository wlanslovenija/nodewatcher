from nodewatcher.modules.monitor.topology import base
from nodewatcher.modules.monitor.topology.pool import pool

pool.register(base.NodeAttribute('t', 'core.type__type'))
