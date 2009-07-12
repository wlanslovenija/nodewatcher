#!/usr/bin/python
#
# WiFi Mesh Monitoring Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wlanlj.settings'

# Import our models
from wlanlj.nodes.models import Node, NodeStatus, Subnet, SubnetStatus, APClient, Link, GraphType, GraphItem, Event, EventSource, EventCode, IfaceType, InstalledPackage, NodeType
from django.db import transaction, models

# Import other stuff
from lib.wifi_utils import OlsrParser, PingParser
from lib.nodewatcher import NodeWatcher
from lib.rra import RRA, RRAIface, RRAClients, RRARTT, RRALinkQuality, RRASolar, RRALoadAverage, RRANumProc, RRAMemUsage, RRALocalTraffic, RRANodesByStatus
from lib.topology import DotTopologyPlotter
from lib.local_stats import fetch_traffic_statistics
from lib import ipcalc
from time import sleep
from datetime import datetime, timedelta
from traceback import format_exc
import pwd
import logging
import time

WORKDIR = "/home/monitor"
GRAPHDIR = "/var/www/nodes.wlan-lj.net/graphs"
RRA_CONF_MAP = {
  GraphType.RTT         : RRARTT,
  GraphType.LQ          : RRALinkQuality,
  GraphType.Clients     : RRAClients,
  GraphType.Traffic     : RRAIface,
  GraphType.LoadAverage : RRALoadAverage,
  GraphType.NumProc     : RRANumProc,
  GraphType.MemUsage    : RRAMemUsage,
  GraphType.Solar       : RRASolar
}

class LastUpdateTimes:
  """
  Stores last update times for stuff that needs to be updated less frequently
  than each 5 minutes.
  """
  uptime_credit = None
  packages = None

lut = {}

@transaction.commit_manually
def main():
  while True:
    try:
      checkMeshStatus()
      checkDeadGraphs()
      checkGlobalStatistics()

      # Repost any events that need reposting
      Event.post_events_that_need_resend()
      
      # Commit transaction if everything went ok
      transaction.commit()
    except:
      logging.warning(format_exc())
      transaction.rollback()

    # Go to sleep for a while
    sleep(60 * 5)

def safe_int_convert(integer):
  """
  A helper method for converting a string to an integer.
  """
  try:
    return int(integer)
  except:
    return None

def safe_loadavg_convert(loadavg):
  """
  A helper method for converting a string to a loadavg tuple.
  """
  try:
    loadavg = loadavg.split(' ')
    la1min, la5min, la15min = (float(x) for x in loadavg[0:3])
    nproc = int(loadavg[3].split('/')[1])
    return la1min, la5min, la15min, nproc
  except:
    return None, None, None, None

def safe_uptime_convert(uptime):
  """
  A helper method for converting a string to an uptime integer.
  """
  try:
    return int(float(uptime.split(' ')[0]))
  except:
    return None

def safe_date_convert(timestamp):
  """
  A helper method for converting a string timestamp into a datetime
  object.
  """
  try:
    return datetime.fromtimestamp(int(timestamp))
  except:
    return None

def add_graph(node, name, type, conf, title, filename, *values, **attrs):
  """
  A helper function for generating graphs.
  """
  rra = str(os.path.join(WORKDIR, 'rra', '%s.rrd' % filename))
  try:
    RRA.update(node, conf, rra, *values)
  except:
    pass
  RRA.graph(conf, title, str(os.path.join(GRAPHDIR, '%s.png' % filename)), *[rra for i in xrange(len(values))])
  
  # Get parent instance (toplevel by default)
  parent = attrs.get('parent', None)

  try:
    graph = GraphItem.objects.get(node = node, name = name, type = type, parent = parent)
  except GraphItem.DoesNotExist:
    graph = GraphItem(node = node, name = name, type = type, parent = parent)
    graph.rra = '%s.rrd' % filename
    graph.graph = '%s.png' % filename
  
  graph.title = title
  graph.last_update = datetime.now()
  graph.dead = False
  graph.save()
  return graph

def checkGlobalStatistics():
  """
  Graph some global statistics.
  """
  stats = fetch_traffic_statistics()
  rra = os.path.join(WORKDIR, 'rra', 'global_replicator_traffic.rrd')
  RRA.update(None, RRALocalTraffic, rra,
    stats['statistics:to-inet'],
    stats['statistics:from-inet'],
    stats['statistics:internal']
  )
  RRA.graph(RRALocalTraffic, 'replicator - Traffic', os.path.join(GRAPHDIR, 'global_replicator_traffic.png'), rra, rra, rra)

  # Nodes by status
  nbs = {}
  for s in Node.objects.all().values('status').annotate(count = models.Count('ip')):
    nbs[s['status']] = s['count']

  rra = os.path.join(WORKDIR, 'rra', 'global_nodes_by_status.rrd')
  RRA.update(None, RRANodesByStatus, rra,
    nbs.get(NodeStatus.Up, 0),
    nbs.get(NodeStatus.Down, 0),
    nbs.get(NodeStatus.Visible, 0),
    nbs.get(NodeStatus.Invalid, 0),
    nbs.get(NodeStatus.Pending, 0),
    nbs.get(NodeStatus.Duped, 0)
  )
  RRA.graph(RRANodesByStatus, 'Nodes By Status', os.path.join(GRAPHDIR, 'global_nodes_by_status.png'), *([rra] * 6))

  # Global client count
  client_count = len(APClient.objects.all())
  rra = os.path.join(WORKDIR, 'rra', 'global_client_count.rrd')
  RRA.update(None, RRAClients, rra, client_count)
  RRA.graph(RRAClients, 'Global Client Count', os.path.join(GRAPHDIR, 'global_client_count.png'), rra)

def checkDeadGraphs():
  """
  Checks for dead graphs.
  """
  for graph in GraphItem.objects.filter(dead = False, last_update__lt = datetime.now() - timedelta(minutes = 10)):
    # Mark graph as dead
    graph.dead = True
    graph.save()

    # Redraw the graph with dead status attached
    pathArchive = str(os.path.join(WORKDIR, 'rra', graph.rra))
    pathImage = str(os.path.join(GRAPHDIR, graph.graph))
    conf = RRA_CONF_MAP[graph.type]

    RRA.graph(conf, str(graph.title), pathImage, end_time = int(time.mktime(graph.last_update.timetuple())), dead = True,
              *[pathArchive for i in xrange(len(conf.sources))])


def checkMeshStatus():
  """
  Performs a mesh status check.
  """
  global lut

  # Remove all invalid nodes and subnets
  Node.objects.filter(status = NodeStatus.Invalid).delete()
  Subnet.objects.filter(status = SubnetStatus.NotAllocated, last_seen__lt = datetime.now() - timedelta(minutes = 11)).delete()
  APClient.objects.filter(last_update__lt = datetime.now() -  timedelta(minutes = 11)).delete()
  GraphItem.objects.filter(last_update__lt = datetime.now() - timedelta(days = 30)).delete()

  # Mark all nodes as down and all subnets as not announced
  Node.objects.all().update(warnings = False)
  Subnet.objects.exclude(status = SubnetStatus.NotAllocated).update(status = SubnetStatus.NotAnnounced)
  Link.objects.all().delete()

  # Fetch routing tables from OLSR
  nodes, hna, aliases = OlsrParser.getTables()

  # Create a topology plotter
  topology = DotTopologyPlotter()

  # Ping nodes present in the database and visible in OLSR
  dbNodes = {}
  nodesToPing = []
  for nodeIp in nodes.keys():
    try:
      # Try to get the node from the database
      dbNodes[nodeIp] = Node.objects.get(ip = nodeIp)
      dbNodes[nodeIp].peers = len(nodes[nodeIp].links)

      # If we have succeeded, add to list
      nodesToPing.append(nodeIp)
    except Node.DoesNotExist:
      # Node does not exist, create an invalid entry for it
      n = Node(ip = nodeIp, status = NodeStatus.Invalid, last_seen = datetime.now())
      n.node_type = NodeType.Unknown
      n.warnings = True
      n.peers = len(nodes[nodeIp].links)
      n.save()
      dbNodes[nodeIp] = n
  
  # Mark invisible nodes as down
  for node in Node.objects.exclude(status = NodeStatus.Invalid):
    oldStatus = node.status

    if node.ip not in dbNodes:
      if node.status == NodeStatus.New:
        node.status = NodeStatus.Pending
      elif node.status != NodeStatus.Pending:
        node.status = NodeStatus.Down
      node.save()

    if oldStatus in (NodeStatus.Up, NodeStatus.Visible, NodeStatus.Duped) and node.status == NodeStatus.Down:
      Event.create_event(node, EventCode.NodeDown, '', EventSource.Monitor)
      
      # Invalidate uptime credit for this node
      nlut = lut.setdefault(node.ip, LastUpdateTimes())
      nlut.uptime_credit = None

  # Setup all node peerings
  for nodeIp, node in nodes.iteritems():
    n = dbNodes[nodeIp]
    oldRedundancyLink = n.redundancy_link
    n.redundancy_link = False

    for peerIp, lq, ilq, etx in node.links:
      l = Link(src = n, dst = dbNodes[peerIp], lq = float(lq), ilq = float(ilq), etx = float(etx))
      l.save()

      # Check if we have a peering with any border routers
      if l.dst.border_router:
        n.redundancy_link = True

    if oldRedundancyLink and not n.redundancy_link:
      Event.create_event(n, EventCode.RedundancyLoss, '', EventSource.Monitor)

    if n.redundancy_req and not n.redundancy_link:
      n.warnings = True

    n.save()
  
  # Add nodes to topology map and generate output
  for node in dbNodes.values():
    topology.addNode(node)

  topology.save(os.path.join(GRAPHDIR, 'mesh_topology.png'))

  # Ping the nodes and update valid node status in the database
  results, dupes = PingParser.pingHosts(10, nodesToPing)
  nodewatcherInfos = NodeWatcher.spawnWorkers(results.keys())
  for nodeIp in nodesToPing:
    n = dbNodes[nodeIp]
    oldStatus = n.status

    # Determine node status
    if nodeIp in results:
      n.status = NodeStatus.Up
      n.rtt_min, n.rtt_avg, n.rtt_max, n.pkt_loss = results[nodeIp]
      
      # Add RTT graph
      add_graph(n, '', GraphType.RTT, RRARTT, 'Latency', 'latency_%s' % nodeIp, n.rtt_avg)

      # Add uptime credit
      nlut = lut.setdefault(n.ip, LastUpdateTimes())
      if nlut.uptime_credit is not None:
        n.uptime_so_far = (n.uptime_so_far or 0) + int(time.time() - nlut.uptime_credit)

      nlut.uptime_credit = time.time()
    else:
      n.status = NodeStatus.Visible

    if nodeIp in dupes:
      n.status = NodeStatus.Duped
      n.warnings = True

    # Generate status change events
    if oldStatus in (NodeStatus.Down, NodeStatus.Pending) and n.status in (NodeStatus.Up, NodeStatus.Visible):
      if oldStatus == NodeStatus.Pending:
        n.first_seen = datetime.now()

      Event.create_event(n, EventCode.NodeUp, '', EventSource.Monitor)
    elif oldStatus != NodeStatus.Duped and n.status == NodeStatus.Duped:
      Event.create_event(n, EventCode.PacketDuplication, '', EventSource.Monitor)
    
    # Add LQ/ILQ graphs
    lq_avg = ilq_avg = 0.0
    for peer in nodes[nodeIp].links:
      lq_avg += float(peer[1])
      ilq_avg += float(peer[2])
    
    lq_graph = add_graph(n, '', GraphType.LQ, RRALinkQuality, 'Link Quality', 'lq_%s' % nodeIp, lq_avg / n.peers, ilq_avg / n.peers)

    for peer in n.src.all():
      add_graph(n, peer.dst.ip, GraphType.LQ, RRALinkQuality, 'Link Quality to %s' % peer.dst, 'lq_peer_%s_%s' % (nodeIp, peer.dst.ip), peer.lq, peer.ilq, parent = lq_graph)

    n.last_seen = datetime.now()

    # Check if we have fetched nodewatcher data
    if nodeIp in nodewatcherInfos and nodewatcherInfos[nodeIp] is not None:
      info = nodewatcherInfos[nodeIp]

      try:
        oldUptime = n.uptime or 0
        oldChannel = n.channel or 0
        oldVersion = n.firmware_version
        n.firmware_version = info['general']['version']
        n.local_time = safe_date_convert(info['general']['local_time'])
        n.bssid = info['wifi']['bssid']
        n.essid = info['wifi']['essid']
        n.channel = NodeWatcher.frequency_to_channel(info['wifi']['frequency'])
        n.clients = 0
        n.uptime = safe_uptime_convert(info['general']['uptime'])

        if oldVersion != n.firmware_version:
          Event.create_event(n, EventCode.VersionChange, '', EventSource.Monitor, data = 'Old version: %s\n  New version: %s' % (oldVersion, n.firmware_version))

        if oldUptime > n.uptime:
          Event.create_event(n, EventCode.UptimeReset, '', EventSource.Monitor, data = 'Old uptime: %s\n  New uptime: %s' % (oldUptime, n.uptime))

        if oldChannel != n.channel and oldChannel != 0:
          Event.create_event(n, EventCode.ChannelChanged, '', EventSource.Monitor, data = 'Old channel: %s\n  New channel %s' % (oldChannel, n.channel))

        if n.has_time_sync_problems():
          n.warnings = True

        # Parse nodogsplash client information
        if 'nds' in info:
          for cid, client in info['nds'].iteritems():
            try:
              c = APClient.objects.get(node = n, ip = client['ip'])
            except APClient.DoesNotExist:
              c = APClient(node = n)
              n.clients_so_far += 1
            
            n.clients += 1
            c.ip = client['ip']
            c.uploaded = safe_int_convert(client['up'])
            c.downloaded = safe_int_convert(client['down'])
            c.last_update = datetime.now()
            c.save()
        
        # Generate a graph for number of clients
        add_graph(n, '', GraphType.Clients, RRAClients, 'Connected Clients', 'clients_%s' % nodeIp, n.clients)

        # Check for IP shortage
        wifiSubnet = n.subnet_set.filter(gen_iface_type = IfaceType.WiFi)
        if len(wifiSubnet) and n.clients >= ipcalc.Network(wifiSubnet[0].subnet, wifiSubnet[0].cidr).size() - 4:
          Event.create_event(n, EventCode.IPShortage, '', EventSource.Monitor, data = 'Subnet: %s\n  Clients: %s' % (wifiSubnet[0], n.clients))

        # Record interface traffic statistics for all interfaces
        for iid, iface in info['iface'].iteritems():
          if iid not in ('wifi0', 'wmaster0'):
            add_graph(n, iid, GraphType.Traffic, RRAIface, 'Traffic - %s' % iid, 'traffic_%s_%s' % (nodeIp, iid), iface['up'], iface['down'])
        
        # Generate load average statistics
        if 'loadavg' in info['general']:
          n.loadavg_1min, n.loadavg_5min, n.loadavg_15min, n.numproc = safe_loadavg_convert(info['general']['loadavg'])
          add_graph(n, '', GraphType.LoadAverage, RRALoadAverage, 'Load Average', 'loadavg_%s' % nodeIp, n.loadavg_1min, n.loadavg_5min, n.loadavg_15min)
          add_graph(n, '', GraphType.NumProc, RRANumProc, 'Number of Processes', 'numproc_%s' % nodeIp, n.numproc)

        # Generate free memory statistics
        if 'memfree' in info['general']:
          n.memfree = safe_int_convert(info['general']['memfree'])
          buffers = safe_int_convert(info['general'].get('buffers', 0))
          cached = safe_int_convert(info['general'].get('cached', 0))
          add_graph(n, '', GraphType.MemUsage, RRAMemUsage, 'Memory Usage', 'memusage_%s' % nodeIp, n.memfree, buffers, cached)

        # Generate solar statistics when available
        if 'solar' in info and all([x in info['solar'] for x in ('batvoltage', 'solvoltage', 'charge', 'state', 'load')]):
          states = {
            'boost'       : 1,
            'equalize'    : 2,
            'absorption'  : 3,
            'float'       : 4
          }
 
          add_graph(n, '', GraphType.Solar, RRASolar, 'Solar Monitor', 'solar_%s' % nodeIp,
            info['solar']['batvoltage'],
            info['solar']['solvoltage'],
            info['solar']['charge'],
            states.get(info['solar']['state'], 1),
            info['solar']['load']
          )

        # Check for installed package versions (every hour)
        nlut = lut.setdefault(n.ip, LastUpdateTimes())
        if not nlut.packages or nlut.packages < datetime.now() - timedelta(hours = 1):
          nlut.packages = datetime.now()
          packages = NodeWatcher.fetchInstalledPackages(n.ip) or {}

          # Remove removed packages and update existing package versions
          for package in n.installedpackage_set.all():
            if package.name not in packages:
              package.delete()
            else:
              package.version = packages[package.name]
              package.last_update = datetime.now()
              package.save()
              del packages[package.name]

          # Add added packages
          for packageName, version in packages.iteritems():
            package = InstalledPackage(node = n)
            package.name = packageName
            package.version = version
            package.last_update = datetime.now()
            package.save()
      except:
        logging.warning(format_exc())

    n.save()

  # Update valid subnet status in the database
  for nodeIp, subnets in hna.iteritems():
    if nodeIp not in dbNodes:
      continue

    for subnet in subnets:
      subnet, cidr = subnet.split("/")

      try:
        s = Subnet.objects.get(node__ip = nodeIp, subnet = subnet, cidr = int(cidr))
        s.last_seen = datetime.now()

        if s.status != SubnetStatus.NotAllocated:
          s.status = SubnetStatus.AnnouncedOk
        elif not s.node.border_router:
          s.node.warnings = True
          s.node.save()

        s.save()
      except Subnet.DoesNotExist:
        # Subnet does not exist, create an invalid entry for it
        s = Subnet(node = dbNodes[nodeIp], subnet = subnet, cidr = int(cidr), last_seen = datetime.now())
        s.status = SubnetStatus.NotAllocated
        s.save()

        # Flag node entry with warnings flag (if not a border router)
        n = dbNodes[nodeIp]
        if not n.border_router:
          n.warnings = True
          n.save()

if __name__ == '__main__':
  info = pwd.getpwnam('monitor')

  # Configure logger
  logging.basicConfig(level = logging.DEBUG,
                      format = '%(asctime)s %(levelname)-8s %(message)s',
                      datefmt = '%a, %d %b %Y %H:%M:%S',
                      filename = '/var/log/wlanlj-monitor.log',
                      filemode = 'a')

  # Change ownership of RRA directory
  os.chown(os.path.join(WORKDIR, 'rra'), info.pw_uid, info.pw_gid)

  # Drop user privileges
  #os.setgid(info.pw_gid)
  #os.setuid(info.pw_uid)

  # Enter main
  main()

