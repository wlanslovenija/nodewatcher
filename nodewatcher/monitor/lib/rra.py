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
    "LINE2:download#A150AA:Download"
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

