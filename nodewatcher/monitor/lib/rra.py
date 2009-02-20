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
    "LINE2:upload#DE0056:Upload",
    r'GPRINT:upload:LAST:  Current\:%8.2lf %s',
    r'GPRINT:upload:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:upload:MAX:Maximum\:%8.2lf %s\n',
    "LINE2:download#A150AA:Download",
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
    r'GPRINT:clients:LAST:  Current\:%8.2lf %s',
    r'GPRINT:clients:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:clients:MAX:Maximum\:%8.2lf %s\n'
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
    "LINE2:rtt#0000ff:RTT",
    r'GPRINT:rtt:LAST:  Current\:%8.2lf %s',
    r'GPRINT:rtt:AVERAGE:Average\:%8.2lf %s',
    r'GPRINT:rtt:MAX:Maximum\:%8.2lf %s\n'
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

