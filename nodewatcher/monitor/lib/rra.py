import rrdtool
import time
import os

class RRAIface:
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

class RRAClients:
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

class RRARTT:
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

class RRALinkQuality:
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

class RRASolar:
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

    "LINE2:batvoltage#6B7FD3:Battery voltage",
    r'GPRINT:batvoltage:LAST:Current\:%8.2lf',
    r'GPRINT:batvoltage:AVERAGE:Average\:%8.2lf',
    r'GPRINT:batvoltage:MAX:Maximum\:%8.2lf\n',
    "LINE2:solvoltage#FF00A3:Solar voltage",
    r'GPRINT:solvoltage:LAST:  Current\:%8.2lf',
    r'GPRINT:solvoltage:AVERAGE:Average\:%8.2lf',
    r'GPRINT:solvoltage:MAX:Maximum\:%8.2lf\n',
    "LINE2:charge#CBFE66:Charge [A]",
    r'GPRINT:charge:LAST:     Current\:%8.2lf',
    r'GPRINT:charge:AVERAGE:Average\:%8.2lf',
    r'GPRINT:charge:MAX:Maximum\:%8.2lf\n',
    "LINE2:load#BAE366:Load [V]",
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
  def update(conf, archive, *values):
    """
    Updates an existing RRD archive or creates a new one if needed.
    """
    if not os.path.isfile(archive):
      rrd = RRA.create(conf, archive)
    else:
      rrd = rrdtool.RoundRobinDatabase(archive)

    rrd.update(rrdtool.Val(*values), template = [x.name for x in conf.sources])
  
  @staticmethod
  def graph(conf, title, graph, *archives):
    """
    Renders a graph from data points.
    """
    g = rrdtool.RoundRobinGraph(graph)
    args = []
    for i, source in enumerate(conf.sources):
      args.append(rrdtool.Def(source.name, archives[i], data_source = source.name, cf = rrdtool.AverageCF))

    args = args + conf.graph
    g.graph(
      alt_y_mrtg = None,
      width = 500,
      height = 120,
      x = "MINUTE:18:MINUTE:72:MINUTE:144:0:%H:%M",
      title = title,
      start = int(time.time() - 86400),
      end = int(time.time() - 180),
      *args
    )

