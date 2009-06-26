import rrdtool
import time
import os

# Models
from wlanlj.nodes.models import StatsSolar
from datetime import datetime

class RRAConfiguration:
  last_update = 0

class RRALocalTraffic(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'toinet',
      type = rrdtool.CounterDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'frominet',
      type = rrdtool.CounterDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'internal',
      type = rrdtool.CounterDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "AREA:toinet#FFD5CC",
    "AREA:frominet#CCFFCC::STACK",
    "AREA:internal#CCE5FF::STACK",
    "LINE1:toinet#CF7E6C:Out     ",
    r'GPRINT:toinet:LAST:Current\:%8.2lf %s',
    r'GPRINT:toinet:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:toinet:MAX:Maximum\:%8.2lf %s\n',
    "LINE1:frominet#6CCF6C:In      :STACK",
    r'GPRINT:frominet:LAST:Current\:%8.2lf %s',
    r'GPRINT:frominet:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:frominet:MAX:Maximum\:%8.2lf %s\n',
    "LINE1:internal#6C9CCF:Internal:STACK",
    r'GPRINT:internal:LAST:Current\:%8.2lf %s',
    r'GPRINT:internal:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:internal:MAX:Maximum\:%8.2lf %s\n'
  ]

class RRANodesByStatus(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'up',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'down',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'visible',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'invalid',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'pending',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'duped',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE1:up#00bb00:up     ",
    r'GPRINT:up:LAST:Current\:%8.2lf',
    r'GPRINT:up:AVERAGE:Average\:%8.2lf',
    r'GPRINT:up:MAX:Maximum\:%8.2lf\n',
    "LINE1:invalid#cccc22:invalid",
    r'GPRINT:invalid:LAST:Current\:%8.2lf',
    r'GPRINT:invalid:AVERAGE:Average\:%8.2lf',
    r'GPRINT:invalid:MAX:Maximum\:%8.2lf\n',
    "LINE1:visible#FFA82F:visible",
    r'GPRINT:visible:LAST:Current\:%8.2lf',
    r'GPRINT:visible:AVERAGE:Average\:%8.2lf',
    r'GPRINT:visible:MAX:Maximum\:%8.2lf\n',
    "LINE1:down#ff0000:down   ",
    r'GPRINT:down:LAST:Current\:%8.2lf',
    r'GPRINT:down:AVERAGE:Average\:%8.2lf',
    r'GPRINT:down:MAX:Maximum\:%8.2lf\n',
    "LINE1:duped#7F43FF:duped  ",
    r'GPRINT:duped:LAST:Current\:%8.2lf',
    r'GPRINT:duped:AVERAGE:Average\:%8.2lf',
    r'GPRINT:duped:MAX:Maximum\:%8.2lf\n',
    "LINE1:pending#648863:pending",
    r'GPRINT:pending:LAST:Current\:%8.2lf',
    r'GPRINT:pending:AVERAGE:Average\:%8.2lf',
    r'GPRINT:pending:MAX:Maximum\:%8.2lf\n',
  ]

class RRAIface(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'upload',
      type = rrdtool.CounterDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'download',
      type = rrdtool.CounterDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE2:upload#DE0056:Upload [B/s]",
    r'GPRINT:upload:LAST:  Current\:%8.2lf %s',
    r'GPRINT:upload:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:upload:MAX:Maximum\:%8.2lf %s\n',
    "LINE2:download#A150AA:Download [B/s]",
    r'GPRINT:download:LAST:Current\:%8.2lf %s',
    r'GPRINT:download:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:download:MAX:Maximum\:%8.2lf %s\n'
  ]

class RRAClients(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'clients',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE2:clients#008310:Clients",
    r'GPRINT:clients:LAST:  Current\:%8.2lf',
    r'GPRINT:clients:AVERAGE:Average\:%8.2lf',
    r'GPRINT:clients:MAX:Maximum\:%8.2lf\n',
    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRARTT(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'rtt',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE1:rtt#0000ff:RTT [ms]",
    r'GPRINT:rtt:LAST:  Current\:%8.2lf',
    r'GPRINT:rtt:AVERAGE:Average\:%8.2lf',
    r'GPRINT:rtt:MAX:Maximum\:%8.2lf\n',
    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRALinkQuality(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'lq',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'ilq',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE1:lq#33ADFF:LQ",
    r'GPRINT:lq:LAST:  Current\:%8.2lf',
    r'GPRINT:lq:AVERAGE:Average\:%8.2lf',
    r'GPRINT:lq:MAX:Maximum\:%8.2lf\n',
    "LINE1:ilq#206C9F:ILQ",
    r'GPRINT:ilq:LAST: Current\:%8.2lf',
    r'GPRINT:ilq:AVERAGE:Average\:%8.2lf',
    r'GPRINT:ilq:MAX:Maximum\:%8.2lf\n',
    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRALoadAverage(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'la1min',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'la5min',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'la15min',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE1:la1min#EACC00:1 Minute",
    r'GPRINT:la1min:LAST:  Current\:%8.2lf',
    r'GPRINT:la1min:AVERAGE:Average\:%8.2lf',
    r'GPRINT:la1min:MAX:Maximum\:%8.2lf\n',
    "LINE1:la5min#EA8F00:5 Minutes",
    r'GPRINT:la5min:LAST: Current\:%8.2lf',
    r'GPRINT:la5min:AVERAGE:Average\:%8.2lf',
    r'GPRINT:la5min:MAX:Maximum\:%8.2lf\n',
    "LINE1:la15min#FF0000:15 Minutes",
    r'GPRINT:la15min:LAST:Current\:%8.2lf',
    r'GPRINT:la15min:AVERAGE:Average\:%8.2lf',
    r'GPRINT:la15min:MAX:Maximum\:%8.2lf\n',
    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRANumProc(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'nproc',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "LINE2:nproc#00CB33:Number of Processes",
    r'GPRINT:nproc:LAST:  Current\:%8.2lf',
    r'GPRINT:nproc:AVERAGE:Average\:%8.2lf',
    r'GPRINT:nproc:MAX:Maximum\:%8.2lf\n',
    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRAMemUsage(RRAConfiguration):
  interval = 300
  sources = [
    rrdtool.DataSource(
      'memfree',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'buffers',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'cached',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    "AREA:memfree#8F005C:Free Memory [KB]",
    r'GPRINT:memfree:LAST:  Current\:%8.2lf',
    r'GPRINT:memfree:AVERAGE:Average\:%8.2lf',
    r'GPRINT:memfree:MAX:Maximum\:%8.2lf\n',
    "AREA:buffers#FF5700:Buffers [KB]:STACK",
    r'GPRINT:buffers:LAST:      Current\:%8.2lf',
    r'GPRINT:buffers:AVERAGE:Average\:%8.2lf',
    r'GPRINT:buffers:MAX:Maximum\:%8.2lf\n',
    "AREA:cached#FFC73B:Cached [KB]:STACK",
    r'GPRINT:cached:LAST:       Current\:%8.2lf',
    r'GPRINT:cached:AVERAGE:Average\:%8.2lf',
    r'GPRINT:cached:MAX:Maximum\:%8.2lf\n'
  ]

class RRASolar(RRAConfiguration):
  db_model = StatsSolar
  interval = 1800
  sources = [
    rrdtool.DataSource(
      'batvoltage',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'solvoltage',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'charge',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'state',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    ),
    rrdtool.DataSource(
      'load',
      type = rrdtool.GaugeDST,
      heartbeat = interval * 2
    )
  ]
  archives = [
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1,
      rows = 180000 / interval
    ),
    rrdtool.RoundRobinArchive(
      cf = rrdtool.AverageCF,
      xff = 0.5,
      steps = 1800 / interval,
      rows = 700
    )
  ]
  graph = [
    # State definitions for background areas
    "CDEF:boost=state,1,EQ,INF,0,IF",
    "CDEF:equalize=state,2,EQ,INF,0,IF",
    "CDEF:absorption=state,3,EQ,INF,0,IF",
    "CDEF:float=state,4,EQ,INF,0,IF",
    "CDEF:inval=state,UN,INF,0,IF",
    
    # Graphical elements
    r"COMMENT:States (background color)\:",
    "AREA:boost#FEF6F6:Boost",
    "AREA:equalize#FEFCE7:Equalize",
    "AREA:absorption#E7EBFE:Absorption",
    r"AREA:float#EDFEED:Float\n",
    "AREA:inval#FFFFFF",

    "LINE2:batvoltage#6B7FD3:Battery [V]",
    r'GPRINT:batvoltage:LAST:    Current\:%8.2lf',
    r'GPRINT:batvoltage:AVERAGE:Average\:%8.2lf',
    r'GPRINT:batvoltage:MAX:Maximum\:%8.2lf\n',
    "LINE2:solvoltage#FF00A3:Solar panel [V]",
    r'GPRINT:solvoltage:LAST:Current\:%8.2lf',
    r'GPRINT:solvoltage:AVERAGE:Average\:%8.2lf',
    r'GPRINT:solvoltage:MAX:Maximum\:%8.2lf\n',
    "LINE2:charge#CBFE66:Charge [A]",
    r'GPRINT:charge:LAST:     Current\:%8.2lf',
    r'GPRINT:charge:AVERAGE:Average\:%8.2lf',
    r'GPRINT:charge:MAX:Maximum\:%8.2lf\n',
    "LINE2:load#BAE366:Load [A]",
    r'GPRINT:load:LAST:       Current\:%8.2lf',
    r'GPRINT:load:AVERAGE:Average\:%8.2lf',
    r'GPRINT:load:MAX:Maximum\:%8.2lf\n',

    '--alt-y-grid',
    '--units-exponent', '0'
  ]

class RRA:
  """
  A wrapper class for managing round-robin archives via RRDTool.
  """
  @staticmethod
  def create(conf, archive):
    """
    Creates a new RRD archive.
    """
    otherArgs = { 'start' : int(time.time()) - 30, 'step' : conf.interval }
    descriptors = [x for x in conf.sources + conf.archives]
    rrd = rrdtool.RoundRobinDatabase(archive)
    rrd.create(*descriptors, **otherArgs)
    return rrd

  @staticmethod
  def update(node, conf, archive, *values):
    """
    Updates an existing RRD archive or creates a new one if needed.
    """
    if not os.path.isfile(archive):
      rrd = RRA.create(conf, archive)
    else:
      rrd = rrdtool.RoundRobinDatabase(archive)

    rrd.update(rrdtool.Val(*values), template = [x.name for x in conf.sources])

    # Record data in database store if set
    now = time.time()
    if 'db_model' in conf.__dict__ and now - conf.last_update >= conf.interval:
      try:
        data = {}
        for i, x in enumerate(conf.sources):
          data[x.name] = values[i]
        
        m = conf.db_model(**data)
        m.node = node
        m.timestamp = datetime.now()
        m.save()
        conf.last_update = now
      except ValueError:
        pass
  
  @staticmethod
  def graph(conf, title, graph, *archives, **kwargs):
    """
    Renders a graph from data points.
    """
    g = rrdtool.RoundRobinGraph(graph)
    args = []
    for i, source in enumerate(conf.sources):
      args.append(rrdtool.Def(source.name, archives[i], data_source = source.name, cf = rrdtool.AverageCF))
    
    if kwargs.get('end_time') is None:
      end_time = int(time.time())
    else:
      end_time = int(kwargs.get('end_time'))

    if kwargs.get('dead') == True:
      args.append('--pango-markup')
      title = '%s <span foreground="red">[OUT OF DATE]</span>' % title

    args = args + conf.graph
    args.append('--font')
    args.append('DEFAULT:0:DejaVu Sans Mono')
    g.graph(
      alt_y_mrtg = None,
      width = 500,
      height = 120,
      x = "MINUTE:18:MINUTE:72:MINUTE:144:0:%H:%M",
      title = title,
      start = end_time - 86400,
      end = end_time - 180,
      *args
    )

