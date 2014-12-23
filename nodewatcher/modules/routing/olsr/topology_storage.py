from nodewatcher.modules.monitor.topology import base
from nodewatcher.modules.monitor.topology.pool import pool

from . import models

pool.register(base.LinkAttribute(models.OlsrTopologyLink, 'proto', models.OLSR_PROTOCOL_NAME))
pool.register(base.LinkAttribute(models.OlsrTopologyLink, 'lq', lambda link: link.lq))
pool.register(base.LinkAttribute(models.OlsrTopologyLink, 'ilq', lambda link: link.ilq))
pool.register(base.LinkAttribute(models.OlsrTopologyLink, 'etx', lambda link: link.etx))
