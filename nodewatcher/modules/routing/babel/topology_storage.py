from nodewatcher.modules.monitor.topology import base
from nodewatcher.modules.monitor.topology.pool import pool

from . import models

pool.register(base.LinkAttribute(models.BabelTopologyLink, 'proto', models.BABEL_PROTOCOL_NAME))
pool.register(base.LinkAttribute(models.BabelTopologyLink, 'rxcost', lambda link: link.rxcost))
pool.register(base.LinkAttribute(models.BabelTopologyLink, 'txcost', lambda link: link.txcost))
pool.register(base.LinkAttribute(models.BabelTopologyLink, 'rttcost', lambda link: link.rttcost))
pool.register(base.LinkAttribute(models.BabelTopologyLink, 'cost', lambda link: link.cost))
