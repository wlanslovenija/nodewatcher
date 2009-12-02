#!/usr/bin/python
#
# WiFi Mesh Monitoring Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

# First parse options (this must be done here since they contain import paths
# that must be parsed before Django models can be imported)
import sys, os
from optparse import OptionParser

print "============================================================================"
print "                  wlan ljubljana Mesh Monitoring Daemon"
print "============================================================================"

parser = OptionParser()
parser.add_option('--path', dest = 'path', help = 'Path that contains "wlanlj" nodewatcher installation')
parser.add_option('--settings', dest = 'settings', help = 'Django settings to use')
parser.add_option('--regenerate-graphs', dest = 'regenerate_graphs', help = 'Just regenerate graphs from RRAs and exit (only graphs that have the redraw flag set are regenerated)', action = 'store_true')
parser.add_option('--stress-test', dest = 'stress_test', help = 'Perform a stress test (only used for development)', action = 'store_true')
options, args = parser.parse_args()

if not options.path:
  print "ERROR: Path specification is required!\n"
  parser.print_help()
  exit(1)
elif not options.settings:
  print "ERROR: Settings specification is required!\n"
  parser.print_help()
  exit(1)

# Setup import paths, since we are using Django models
sys.path.append(options.path)
os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

# Import our models
from wlanlj.nodes.models import Node, NodeStatus, Subnet, SubnetStatus, APClient, Link, GraphType, GraphItem, Event, EventSource, EventCode, IfaceType, InstalledPackage, NodeType, RenumberNotice
from django.db import transaction, models, connection
from django.conf import settings

# Import other stuff
if (hasattr(settings, 'MONITOR_ENABLE_SIMULATION') and settings.MONITOR_ENABLE_SIMULATION) or options.stress_test:
  from simulator import nodewatcher, wifi_utils
else:
  from lib import nodewatcher, wifi_utils

from lib.rra import RRA, RRAIface, RRAClients, RRARTT, RRALinkQuality, RRASolar, RRALoadAverage, RRANumProc, RRAMemUsage, RRALocalTraffic, RRANodesByStatus, RRAWifiCells, RRAOlsrPeers
from lib.topology import DotTopologyPlotter
from lib.local_stats import fetch_traffic_statistics
from lib import ipcalc
from time import sleep
from datetime import datetime, timedelta
from traceback import format_exc, print_exc
import pwd
import logging
import time
import multiprocessing
import gc

RRA_CONF_MAP = {
  GraphType.RTT         : RRARTT,
  GraphType.LQ          : RRALinkQuality,
  GraphType.Clients     : RRAClients,
  GraphType.Traffic     : RRAIface,
  GraphType.LoadAverage : RRALoadAverage,
  GraphType.NumProc     : RRANumProc,
  GraphType.MemUsage    : RRAMemUsage,
  GraphType.Solar       : RRASolar,
  GraphType.WifiCells   : RRAWifiCells,
  GraphType.OlsrPeers   : RRAOlsrPeers
}
WORKER_POOL = None

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
  if hasattr(settings, 'MONITOR_DISABLE_GRAPHS') and settings.MONITOR_DISABLE_GRAPHS:
    return
  
  # Get parent instance (toplevel by default)
  parent = attrs.get('parent', None)

  try:
    graph = GraphItem.objects.get(node = node, name = name, type = type, parent = parent)
  except GraphItem.DoesNotExist:
    graph = GraphItem(node = node, name = name, type = type, parent = parent)
    graph.rra = '%s_%s.rrd' % (filename, node.pk)
    graph.graph = '%s_%s.png' % (filename, node.pk)
  
  rra = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
  try:
    RRA.update(node, conf, rra, *values)
  except:
    pass
  
  graph.title = title
  graph.last_update = datetime.now()
  graph.dead = False
  graph.need_redraw = True
  graph.save()
  return graph

@transaction.commit_on_success
def check_events():
  """
  Check events that need resend.
  """
  transaction.set_dirty()
  Event.post_events_that_need_resend()

@transaction.commit_on_success
def check_global_statistics():
  """
  Graph some global statistics.
  """
  transaction.set_dirty()

  try:
    stats = fetch_traffic_statistics()
    rra = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_replicator_traffic.rrd')
    RRA.update(None, RRALocalTraffic, rra,
      stats['statistics:to-inet'],
      stats['statistics:from-inet'],
      stats['statistics:internal']
    )
  except:
    logging.warning("Unable to process local server traffic information, skipping!")

  # Nodes by status
  nbs = {}
  for s in Node.objects.exclude(node_type = NodeType.Test).values('status').annotate(count = models.Count('ip')):
    nbs[s['status']] = s['count']

  rra = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_nodes_by_status.rrd')
  RRA.update(None, RRANodesByStatus, rra,
    nbs.get(NodeStatus.Up, 0),
    nbs.get(NodeStatus.Down, 0),
    nbs.get(NodeStatus.Visible, 0),
    nbs.get(NodeStatus.Invalid, 0),
    nbs.get(NodeStatus.Pending, 0),
    nbs.get(NodeStatus.Duped, 0)
  )

  # Global client count
  client_count = len(APClient.objects.all())
  rra = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_client_count.rrd')
  RRA.update(None, RRAClients, rra, client_count)

@transaction.commit_on_success
def regenerate_graph(graph):
  """
  Regenerates a single graph.
  """
  pathArchive = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
  pathImage = graph.graph
  conf = RRA_CONF_MAP[graph.type]
  
  try:
    RRA.graph(conf, str(graph.title), pathImage, pathArchive, end_time = int(time.mktime(graph.last_update.timetuple())), dead = graph.dead)
    
    # Graph has been regenerated, mark it as such
    graph.need_redraw = False
    graph.save()
  except:
    pass

def regenerate_global_statistics_graphs():
  """
  Regenerates global statistics graphs.
  """
  rra_traffic = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_replicator_traffic.rrd')
  rra_status = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_nodes_by_status.rrd')
  rra_clients = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_client_count.rrd')
  
  try:
    RRA.graph(RRALocalTraffic, 'replicator - Traffic', 'global_replicator_traffic.png', rra_traffic)
    RRA.graph(RRANodesByStatus, 'Nodes By Status', 'global_nodes_by_status.png', rra_status)
    RRA.graph(RRAClients, 'Global Client Count', 'global_client_count.png', rra_clients)
  except:
    logging.warning("Unable to regenerate some global statistics graphs!")

def regenerate_graphs():
  """
  Regenerates all graphs from RRAs.
  """
  # We must close the database connection before we fork the worker pool, otherwise
  # resources will be shared and problems will arise!
  connection.close()
  pool = multiprocessing.Pool(processes = settings.MONITOR_GRAPH_WORKERS)
  
  try:
    pool.map(regenerate_graph, GraphItem.objects.filter(need_redraw = True)[:])
    pool.apply(regenerate_global_statistics_graphs)
  except:
    logging.warning(format_exc())
  
  pool.close()
  pool.join()

@transaction.commit_on_success
def check_dead_graphs():
  """
  Checks for dead graphs.
  """
  GraphItem.objects.filter(dead = False, last_update__lt = datetime.now() - timedelta(minutes = 10)).update(
    dead = True,
    need_redraw = True
  )
  
  # Remove RRDs that need removal
  for graph in GraphItem.objects.filter(need_removal = True):
    try:
      os.unlink(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
    except:
      pass
  
  GraphItem.objects.filter(need_removal = True).delete()

@transaction.commit_on_success
def process_node(node_ip, ping_results, is_duped, peers):
  """
  Processes a single node.

  @param node_ip: Node's IP address
  @param ping_results: Results obtained from ICMP ECHO tests
  @param is_duped: True if duplicate echos received
  @param peers: Peering info from routing daemon
  """
  transaction.set_dirty()
  n = Node.objects.get(ip = node_ip)
  oldStatus = n.status

  # Determine node status
  if ping_results is not None:
    n.status = NodeStatus.Up
    n.rtt_min, n.rtt_avg, n.rtt_max, n.pkt_loss = ping_results
    
    # Add RTT graph
    add_graph(n, '', GraphType.RTT, RRARTT, 'Latency', 'latency', n.rtt_avg)

    # Add uptime credit
    if n.uptime_last:
      n.uptime_so_far = (n.uptime_so_far or 0) + (datetime.now() - n.uptime_last).seconds
    
    n.uptime_last = datetime.now()
  else:
    n.status = NodeStatus.Visible

  if is_duped:
    n.status = NodeStatus.Duped
    n.warnings = True

  # Generate status change events
  if oldStatus in (NodeStatus.Down, NodeStatus.Pending, NodeStatus.New) and n.status in (NodeStatus.Up, NodeStatus.Visible):
    if oldStatus in (NodeStatus.New, NodeStatus.Pending):
      n.first_seen = datetime.now()

    Event.create_event(n, EventCode.NodeUp, '', EventSource.Monitor)
  elif oldStatus != NodeStatus.Duped and n.status == NodeStatus.Duped:
    Event.create_event(n, EventCode.PacketDuplication, '', EventSource.Monitor)
  
  # Add olsr peer count graph
  add_graph(n, '', GraphType.OlsrPeers, RRAOlsrPeers, 'Routing Peers', 'olsrpeers', n.peers)

  # Add LQ/ILQ graphs
  if n.peers > 0:
    lq_avg = ilq_avg = 0.0
    for peer in peers:
      lq_avg += float(peer[1])
      ilq_avg += float(peer[2])
    
    lq_graph = add_graph(n, '', GraphType.LQ, RRALinkQuality, 'Average Link Quality', 'lq', lq_avg / n.peers, ilq_avg / n.peers)

    for peer in n.src.all():
      add_graph(n, peer.dst.ip, GraphType.LQ, RRALinkQuality, 'Link Quality to %s' % peer.dst, 'lq_peer_%s' % peer.dst.pk, peer.lq, peer.ilq, parent = lq_graph)

  n.last_seen = datetime.now()

  # Check if we have fetched nodewatcher data
  info = nodewatcher.fetch_node_info(node_ip)
  if info is not None and 'general' in info:
    try:
      oldUptime = n.uptime or 0
      oldChannel = n.channel or 0
      oldVersion = n.firmware_version
      n.firmware_version = info['general']['version']
      n.local_time = safe_date_convert(info['general']['local_time'])
      n.bssid = info['wifi']['bssid']
      n.essid = info['wifi']['essid']
      n.channel = nodewatcher.frequency_to_channel(info['wifi']['frequency'])
      n.clients = 0
      n.uptime = safe_uptime_convert(info['general']['uptime'])
      
      if 'uuid' in info['general']:
        n.reported_uuid = info['general']['uuid']
        if n.reported_uuid and n.reported_uuid != n.uuid:
          n.warnings = True

      if oldVersion != n.firmware_version:
        Event.create_event(n, EventCode.VersionChange, '', EventSource.Monitor, data = 'Old version: %s\n  New version: %s' % (oldVersion, n.firmware_version))

      if oldUptime > n.uptime:
        Event.create_event(n, EventCode.UptimeReset, '', EventSource.Monitor, data = 'Old uptime: %s\n  New uptime: %s' % (oldUptime, n.uptime))

      if oldChannel != n.channel and oldChannel != 0:
        Event.create_event(n, EventCode.ChannelChanged, '', EventSource.Monitor, data = 'Old channel: %s\n  New channel %s' % (oldChannel, n.channel))

      if n.has_time_sync_problems():
        n.warnings = True
      
      # Parse nodogsplash client information
      oldNdsStatus = n.captive_portal_status
      if 'nds' in info:
        if 'down' in info['nds'] and info['nds']['down'] == '1':
          n.captive_portal_status = False
          n.warnings = True
        else:
          n.captive_portal_status = True

          for cid, client in info['nds'].iteritems():
            if not cid.startswith('client'):
              continue

            try:
              c = APClient.objects.get(node = n, ip = client['ip'])
            except APClient.DoesNotExist:
              c = APClient(node = n)
              n.clients_so_far += 1
            
            n.clients += 1
            c.ip = client['ip']
            c.connected_at = safe_date_convert(client['added_at'])
            c.uploaded = safe_int_convert(client['up'])
            c.downloaded = safe_int_convert(client['down'])
            c.last_update = datetime.now()
            c.save()
      else:
        n.captive_portal_status = True
      
      # Check for captive portal status change
      if oldNdsStatus and not n.captive_portal_status:
        Event.create_event(n, EventCode.CaptivePortalDown, '', EventSource.Monitor)
      elif not oldNdsStatus and n.captive_portal_status:
        Event.create_event(n, EventCode.CaptivePortalUp, '', EventSource.Monitor)

      # Generate a graph for number of wifi cells
      if 'cells' in info['wifi']:
        add_graph(n, '', GraphType.WifiCells, RRAWifiCells, 'Nearby Wifi Cells', 'wificells', safe_int_convert(info['wifi']['cells']) or 0)

      # Update node's MAC address on wifi iface
      if 'mac' in info['wifi']:
        n.wifi_mac = info['wifi']['mac']

      # Check for VPN statistics
      if 'vpn' in info:
        n.vpn_mac = info['vpn']['mac']

      # Generate a graph for number of clients
      add_graph(n, '', GraphType.Clients, RRAClients, 'Connected Clients', 'clients', n.clients)

      # Check for IP shortage
      wifiSubnet = n.subnet_set.filter(gen_iface_type = IfaceType.WiFi, allocated = True)
      if len(wifiSubnet) and n.clients >= ipcalc.Network(wifiSubnet[0].subnet, wifiSubnet[0].cidr).size() - 4:
        Event.create_event(n, EventCode.IPShortage, '', EventSource.Monitor, data = 'Subnet: %s\n  Clients: %s' % (wifiSubnet[0], n.clients))

      # Record interface traffic statistics for all interfaces
      for iid, iface in info['iface'].iteritems():
        if iid not in ('wifi0', 'wmaster0'):
          add_graph(n, iid, GraphType.Traffic, RRAIface, 'Traffic - %s' % iid, 'traffic_%s' % iid, iface['up'], iface['down'])
      
      # Generate load average statistics
      if 'loadavg' in info['general']:
        n.loadavg_1min, n.loadavg_5min, n.loadavg_15min, n.numproc = safe_loadavg_convert(info['general']['loadavg'])
        add_graph(n, '', GraphType.LoadAverage, RRALoadAverage, 'Load Average', 'loadavg', n.loadavg_1min, n.loadavg_5min, n.loadavg_15min)
        add_graph(n, '', GraphType.NumProc, RRANumProc, 'Number of Processes', 'numproc', n.numproc)

      # Generate free memory statistics
      if 'memfree' in info['general']:
        n.memfree = safe_int_convert(info['general']['memfree'])
        buffers = safe_int_convert(info['general'].get('buffers', 0))
        cached = safe_int_convert(info['general'].get('cached', 0))
        add_graph(n, '', GraphType.MemUsage, RRAMemUsage, 'Memory Usage', 'memusage', n.memfree, buffers, cached)

      # Generate solar statistics when available
      if 'solar' in info and all([x in info['solar'] for x in ('batvoltage', 'solvoltage', 'charge', 'state', 'load')]):
        states = {
          'boost'       : 1,
          'equalize'    : 2,
          'absorption'  : 3,
          'float'       : 4
        }

        add_graph(n, '', GraphType.Solar, RRASolar, 'Solar Monitor', 'solar',
          info['solar']['batvoltage'],
          info['solar']['solvoltage'],
          info['solar']['charge'],
          states.get(info['solar']['state'], 1),
          info['solar']['load']
        )

      # Check for installed package versions (every hour)
      try:
        last_pkg_update = n.installedpackage_set.all()[0].last_update
      except:
        last_pkg_update = None

      if not last_pkg_update or last_pkg_update < datetime.now() - timedelta(hours = 1):
        packages = nodewatcher.fetch_installed_packages(n.ip) or {}

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
      
      # Check if DNS works
      if 'dns' in info:
        old_dns_works = n.dns_works
        n.dns_works = info['dns']['local'] == '0' and info['dns']['remote'] == '0'
        if not n.dns_works:
          n.warnings = True

        if old_dns_works != n.dns_works:
          # Generate a proper event when the state changes
          if n.dns_works:
            Event.create_event(n, EventCode.DnsResolverRestored, '', EventSource.Monitor)
          else:
            Event.create_event(n, EventCode.DnsResolverFailed, '', EventSource.Monitor)
    except:
      logging.warning(format_exc())

  n.save()
  
  # When GC debugging is enabled perform some more work
  if hasattr(settings, 'MONITOR_ENABLE_GC_DEBUG') and settings.MONITOR_ENABLE_GC_DEBUG:
    gc.collect()
    return os.getpid(), len(gc.get_objects())
  
  return None, None

@transaction.commit_on_success
def check_mesh_status():
  """
  Performs a mesh status check.
  """
  # Initialize the state of nodes and subnets, remove out of date ap clients and graph items
  Node.objects.filter(status__in = (NodeStatus.Invalid, NodeStatus.AwaitingRenumber)).update(visible = False)
  Subnet.objects.all().update(visible = False)
  APClient.objects.filter(last_update__lt = datetime.now() -  timedelta(minutes = 11)).delete()
  GraphItem.objects.filter(last_update__lt = datetime.now() - timedelta(days = 30)).delete()

  # Mark all nodes as down
  Node.objects.all().update(warnings = False, conflicting_subnets = False)
  Link.objects.all().delete()

  # Fetch routing tables from OLSR
  nodes, hna = wifi_utils.get_tables(settings.MONITOR_OLSR_HOST)

  # Ping nodes present in the database and visible in OLSR
  dbNodes = {}
  nodesToPing = []
  for nodeIp in nodes.keys():
    try:
      # Try to get the node from the database
      n = Node.objects.get(ip = nodeIp)
      n.visible = True
      n.peers = len(nodes[nodeIp].links)

      # If we have succeeded, add to list (if not invalid)
      if not n.is_invalid():
        if n.awaiting_renumber:
          # Reset any status from awaiting renumber to invalid
          for notice in n.renumber_notices.all():
            try:
              rn = Node.objects.get(ip = notice.original_ip)
              if rn.status == NodeStatus.AwaitingRenumber:
                rn.status = NodeStatus.Invalid
                rn.node_type = NodeType.Unknown
                rn.awaiting_renumber = False
                rn.save()
            except Node.DoesNotExist:
              pass
            
            notice.delete()
          
          n.awaiting_renumber = False
          n.save()
        
        nodesToPing.append(nodeIp)
      else:
        n.last_seen = datetime.now()
        n.peers = len(nodes[nodeIp].links)
        n.save()
      
      dbNodes[nodeIp] = n
    except Node.DoesNotExist:
      # Node does not exist, create an invalid entry for it
      n = Node(ip = nodeIp, status = NodeStatus.Invalid, last_seen = datetime.now())
      n.visible = True
      n.node_type = NodeType.Unknown
      n.warnings = True
      n.peers = len(nodes[nodeIp].links)
      
      # Check if there are any renumber notices for this IP address
      try:
        notice = RenumberNotice.objects.get(original_ip = nodeIp)
        n.status = NodeStatus.AwaitingRenumber
        n.node_type = notice.node.node_type
        n.awaiting_renumber = True
      except RenumberNotice.DoesNotExist:
        pass
      
      n.save()
      dbNodes[nodeIp] = n

      # Create an event since an unknown node has appeared
      Event.create_event(n, EventCode.UnknownNodeAppeared, '', EventSource.Monitor)
  
  # Mark invisible nodes as down
  for node in Node.objects.exclude(status__in = (NodeStatus.Invalid, NodeStatus.AwaitingRenumber)):
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
      node.uptime_last = None
      node.save()
  
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
    
    if not n.is_invalid():
      if oldRedundancyLink and not n.redundancy_link:
        Event.create_event(n, EventCode.RedundancyLoss, '', EventSource.Monitor)
      elif not oldRedundancyLink and n.redundancy_link:
        Event.create_event(n, EventCode.RedundancyRestored, '', EventSource.Monitor)

    if n.redundancy_req and not n.redundancy_link:
      n.warnings = True

    n.save()
  
  # Add nodes to topology map and generate output
  if hasattr(settings, 'MONITOR_DISABLE_GRAPHS') and settings.MONITOR_DISABLE_GRAPHS:
    pass
  else:
    # Only generate topology when graphing is not disabled
    topology = DotTopologyPlotter()
    for node in dbNodes.values():
      topology.addNode(node)

    topology.save(os.path.join(settings.GRAPH_DIR, 'mesh_topology.png'))

  # Update valid subnet status in the database
  for nodeIp, subnets in hna.iteritems():
    if nodeIp not in dbNodes:
      continue

    for subnet in subnets:
      subnet, cidr = subnet.split("/")

      try:
        s = Subnet.objects.get(node__ip = nodeIp, subnet = subnet, cidr = int(cidr))
        s.last_seen = datetime.now()
        s.visible = True
        
        if s.status == SubnetStatus.Subset:
          pass
        elif s.status in (SubnetStatus.AnnouncedOk, SubnetStatus.NotAnnounced):
          s.status = SubnetStatus.AnnouncedOk
        elif not s.node.border_router or s.status == SubnetStatus.Hijacked:
          s.node.warnings = True
          s.node.save()

        s.save()
      except Subnet.DoesNotExist:
        # Subnet does not exist, prepare one
        s = Subnet(node = dbNodes[nodeIp], subnet = subnet, cidr = int(cidr), last_seen = datetime.now())
        s.visible = True

        # Check if this is a more specific prefix announce for an allocated prefix
        if Subnet.objects.ip_filter(ip_subnet__contains = '%s/%s' % (subnet, cidr)).filter(node = s.node, allocated = True).count() > 0:
          s.status = SubnetStatus.Subset
        else:
          s.status = SubnetStatus.NotAllocated
        s.save()

        # Check if this is a hijack
        n = dbNodes[nodeIp]
        try:
          origin = Subnet.objects.ip_filter(
            # Subnet overlaps with another one
            ip_subnet__contains = '%s/%s' % (subnet, cidr)
          ).exclude(
            # Of another node (= filter all subnets belonging to current node)
            node = s.node
          ).get(
            # That is allocated and visible
            allocated = True,
            visible = True
          )
          s.status = SubnetStatus.Hijacked
          s.save()

          # Generate an event
          Event.create_event(n, EventCode.SubnetHijacked, '', EventSource.Monitor,
                             data = 'Subnet: %s/%s\n  Allocated to: %s' % (s.subnet, s.cidr, origin.node))
        except Subnet.DoesNotExist:
          pass
        
        # Flag node entry with warnings flag (if not a border router)
        if s.status != SubnetStatus.Subset and (not n.border_router or s.status == SubnetStatus.Hijacked):
          n.warnings = True
          n.save()
      
      # Detect subnets that cause conflicts and raise warning flags for all involved
      # nodes
      if s.is_conflicting():
        s.node.warnings = True
        s.node.conflicting_subnets = True
        s.node.save()
        
        for cs in s.get_conflicting_subnets():
          cs.node.warnings = True
          cs.node.conflicting_subnets = True
          cs.node.save()
  
  # Remove (or change their status) subnets that are not visible
  Subnet.objects.filter(status__in = (SubnetStatus.NotAllocated, SubnetStatus.Subset), visible = False).delete()
  Subnet.objects.filter(status = SubnetStatus.AnnouncedOk, visible = False).update(status = SubnetStatus.NotAnnounced)

  # Remove subnets that were hijacked but are not visible anymore
  for s in Subnet.objects.filter(status = SubnetStatus.Hijacked, visible = False):
    Event.create_event(s.node, EventCode.SubnetRestored, '', EventSource.Monitor, data = 'Subnet: %s/%s' % (s.subnet, s.cidr))
    s.delete()
  
  # Remove invisible unknown nodes
  for node in Node.objects.filter(status = NodeStatus.Invalid, visible = False).all():
    # Create an event since an unknown node has disappeared
    Event.create_event(node, EventCode.UnknownNodeDisappeared, '', EventSource.Monitor)

  Node.objects.filter(status__in = (NodeStatus.Invalid, NodeStatus.AwaitingRenumber), visible = False).delete()

  # Ping the nodes to prepare information for later node processing
  results, dupes = wifi_utils.ping_hosts(10, nodesToPing)
  
  if hasattr(settings, 'MONITOR_DISABLE_MULTIPROCESSING') and settings.MONITOR_DISABLE_MULTIPROCESSING:
    # Multiprocessing is disabled (the MONITOR_DISABLE_MULTIPROCESSING option is usually
    # used for debug purpuses where a single process is prefered)
    for node_ip in nodesToPing:
      process_node(node_ip, results.get(node_ip), node_ip in dupes, nodes[node_ip].links)
    
    # Commit the transaction here since we do everything in the same session
    transaction.commit()
  else:
    # We MUST commit the current transaction here, because we will be processing
    # some transactions in parallel and must ensure that this transaction that has
    # modified the nodes is commited. Otherwise this will deadlock!
    transaction.commit()
    
    worker_results = []
    for node_ip in nodesToPing:
      worker_results.append(
        WORKER_POOL.apply_async(process_node, (node_ip, results.get(node_ip), node_ip in dupes, nodes[node_ip].links))
      )
    
    # Wait for all workers to finish processing
    objects = {}
    for result in worker_results:
      try:
        k, v = result.get()
        objects[k] = v
      except Exception, e:
        logging.warning(format_exc())
    
    # When GC debugging is enabled make some additional computations
    if hasattr(settings, 'MONITOR_ENABLE_GC_DEBUG') and settings.MONITOR_ENABLE_GC_DEBUG:
      global _MAX_GC_OBJCOUNT
      objcount = sum(objects.values())
      
      if '_MAX_GC_OBJCOUNT' not in globals():
        _MAX_GC_OBJCOUNT = objcount
      
      logging.debug("GC object count: %d %s" % (objcount, "!M" if objcount > _MAX_GC_OBJCOUNT else ""))
      _MAX_GC_OBJCOUNT = max(_MAX_GC_OBJCOUNT, objcount)

if __name__ == '__main__':
  # Configure logger
  logging.basicConfig(level = logging.DEBUG,
                      format = '%(asctime)s %(levelname)-8s %(message)s',
                      datefmt = '%a, %d %b %Y %H:%M:%S',
                      filename = settings.MONITOR_LOGFILE,
                      filemode = 'a')
  
  try:
    info = getpwnam(settings.MONITOR_USER)
    
    # Change ownership of RRA directory
    os.chown(os.path.join(settings.MONITOR_WORKDIR, 'rra'), info.pw_uid, info.pw_gid)
    
    # Drop user privileges
    #os.setgid(info.pw_gid)
    #os.setuid(info.pw_uid)
  except:
    logging.warning("Failed to chown monitor RRA storage directory!")

  # Check if we should just regenerate the graphs
  if options.regenerate_graphs:
    # Regenerate all graphs that need redrawing
    print ">>> Regenerating graphs from RRAs..."
    regenerate_graphs()
    print ">>> Graph generation completed."
    exit(0)
  
  # Check if we should just perform stress testing
  if options.stress_test:
    print ">>> Performing stress test..."
    
    # Force some settings
    settings.MONITOR_ENABLE_SIMULATION = True
    settings.MONITOR_DISABLE_MULTIPROCESSING = True
    
    # Check mesh status in a tight loop
    try:
      for i in xrange(1000):
        check_mesh_status()
        check_dead_graphs()
        check_events()
        
        # Output progress messages
        if i > 0 and i % 10 == 0:
          print "  > Completed %d iterations. (%d gc objects)" % (i, len(gc.get_objects()))
    except KeyboardInterrupt:
      print "!!! Aborted by user."
      exit(1)
    except:
      print "!!! Unhandled exception."
      print_exc()
      exit(1)
    
    print ">>> Stress test completed."
    exit(0)
  
  # Output warnings when debug mode is enabled
  if settings.DEBUG:
    logging.warning("Debug mode is enabled, monitor will leak memory!")
  
  if hasattr(settings, 'MONITOR_ENABLE_SIMULATION') and settings.MONITOR_ENABLE_SIMULATION:
    logging.warning("All feeds are being simulated!")
  
  if hasattr(settings, 'MONITOR_DISABLE_MULTIPROCESSING') and settings.MONITOR_DISABLE_MULTIPROCESSING:
    logging.warning("Multiprocessing mode disabled.")
  
  if hasattr(settings, 'MONITOR_DISABLE_GRAPHS') and settings.MONITOR_DISABLE_GRAPHS:
    logging.warning("Graph generation disabled.")
  
  if hasattr(settings, 'MONITOR_ENABLE_GC_DEBUG') and settings.MONITOR_ENABLE_GC_DEBUG:
    logging.warning("Garbage collection debugging enabled.")
  
  # Create worker pool and start processing
  logging.info("wlan ljubljana mesh monitoring system is initializing...")
  WORKER_POOL = multiprocessing.Pool(processes = settings.MONITOR_WORKERS)
  try:
    while True:
      # Perform all processing
      try:
        check_mesh_status()
        check_dead_graphs()
        check_global_statistics()
        check_events()
        
        if hasattr(settings, 'MONITOR_DISABLE_GRAPHS') and settings.MONITOR_DISABLE_GRAPHS:
          pass
        else:
          regenerate_graphs()
      except:
        logging.warning(format_exc())
      
      # Go to sleep for a while
      sleep(settings.MONITOR_POLL_INTERVAL)
  except:
    logging.warning("Terminating workers...")
    WORKER_POOL.terminate()

