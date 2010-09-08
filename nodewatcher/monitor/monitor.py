#!/usr/bin/python
#
# nodewatcher monitoring daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

# First parse options (this must be done here since they contain import paths
# that must be parsed before Django models can be imported)
import sys, os
from optparse import OptionParser

print "============================================================================"
print "                       nodewatcher monitoring daemon                        "
print "============================================================================"

parser = OptionParser()
parser.add_option('--path', dest = 'path', help = 'Path that contains nodewatcher "web" Python module')
parser.add_option('--settings', dest = 'settings', help = 'Django settings to use')
parser.add_option('--olsr-host', dest = 'olsr_host', help = 'A host with OLSR txt-info plugin running (overrides settings file)')
parser.add_option('--regenerate-graphs', dest = 'regenerate_graphs', help = 'Just regenerate graphs from RRAs and exit (only graphs that have the redraw flag set are regenerated)', action = 'store_true')
parser.add_option('--stress-test', dest = 'stress_test', help = 'Perform a stress test (only used for development)', action = 'store_true')
parser.add_option('--collect-simulation', dest = 'collect_sim', help = 'Collect simulation data', action = 'store_true')
parser.add_option('--update-rrds', dest = 'update_rrds', help = 'Update RRDs', action = 'store_true')
parser.add_option('--update-rrd-type', dest = 'update_rrd_type', help = 'Update RRD type (refresh, archive)', default = 'refresh')
parser.add_option('--reverse-populate', dest = 'reverse_populate', help = 'Reverse populate RRD with data from a database', action = 'store_true')
parser.add_option('--reverse-populate-node', dest = 'rp_node', help = 'Node to populate data for')
parser.add_option('--reverse-populate-graph', dest = 'rp_graph', help = 'Graph type to populate data for')
options, args = parser.parse_args()

if not options.path:
  print "ERROR: Path specification is required!\n"
  parser.print_help()
  exit(1)
elif not options.settings:
  print "ERROR: Settings specification is required!\n"
  parser.print_help()
  exit(1)
elif options.reverse_populate and (not options.rp_node or not options.rp_graph):
  print "ERROR: Reverse populate requires node and graph type!\n"
  parser.print_help()
  exit(1)

# Setup import paths, since we are using Django models
sys.path.append(options.path)
os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

# Import our models
from web.nodes.models import Node, NodeStatus, Subnet, SubnetStatus, APClient, Link, GraphType, GraphItem, Event, EventSource, EventCode, IfaceType, InstalledPackage, NodeType, RenumberNotice, WarningCode, NodeWarning, Tweet
from web.generator.models import Template, Profile
from web.nodes import data_archive
from django.db import transaction, models, connection
from django.conf import settings

# Possibly override MONITOR_OLSR_HOST setting with comomand line option
if options.olsr_host:
  settings.MONITOR_OLSR_HOST = options.olsr_host

# Import other stuff
if getattr(settings, 'MONITOR_ENABLE_SIMULATION', None) or options.stress_test:
  from simulator import nodewatcher, wifi_utils
else:
  from lib import nodewatcher, wifi_utils
  
  # Setup simulation data collection
  nodewatcher.COLLECT_SIMULATION_DATA = options.collect_sim
  wifi_utils.COLLECT_SIMULATION_DATA = options.collect_sim

from lib.rra import *
from lib.topology import DotTopologyPlotter
from lib.local_stats import fetch_traffic_statistics
from lib.graphs import Grapher, RRA_CONF_MAP
from lib import ipcalc
from time import sleep
from datetime import datetime, timedelta
from traceback import format_exc, print_exc
import pwd
import logging
import time
import multiprocessing
import gc
import struct

if Tweet.tweets_enabled():
  from lib import bitly


WORKER_POOL = None

def safe_int_convert(integer):
  """
  A helper method for converting a string to an integer.
  """
  try:
    return int(integer)
  except:
    return None

def safe_float_convert(value, precision = 3):
  """
  A helper method for converting a string to a float.
  """
  try:
    return round(float(value), precision)
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

def safe_dbm_convert(dbm):
  """
  A helper method for converting a string into a valid dBm integer
  value. This also takes care of unsigned/signed char conversions.
  """
  try:
    dbm = safe_int_convert(dbm)
    if dbm is None:
      return None
    
    if dbm > 127:
      # Convert from unsigned char into signed one
      dbm = struct.unpack("b", struct.pack("<i", dbm)[0])[0]
    
    return dbm
  except:
    return None

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
      stats['statistics:internal'],
      graph = -1
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
    nbs.get(NodeStatus.Duped, 0),
    graph = -2
  )

  # Global client count
  client_count = len(APClient.objects.all())
  rra = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_client_count.rrd')
  RRA.update(None, RRAGlobalClients, rra, client_count, graph = -3)

@transaction.commit_on_success
def regenerate_graph(graph):
  """
  Regenerates a single graph.
  """
  pathArchive = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
  pathImage = graph.graph
  conf = RRA_CONF_MAP[graph.type]
  
  try:
    RRA.graph(conf, str(graph.title), pathImage, pathArchive, end_time = int(time.mktime(graph.last_update.timetuple())), dead = graph.dead, last_update = graph.last_update)
    
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
    RRA.graph(RRANodesByStatus, 'Nodes By Status', 'global_nodes_by_status.png', rra_status)
    RRA.graph(RRAGlobalClients, 'Global Connected Clients', 'global_client_count.png', rra_clients)
    RRA.graph(RRALocalTraffic, 'replicator - Traffic', 'global_replicator_traffic.png', rra_traffic) # This should be last as it can fail on installations for local development
  except:
    logging.warning("Unable to regenerate some global statistics graphs!")

def update_rrd(item):
  """
  Updates a single RRD.
  """
  archive = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', item.rra))
  conf = RRA_CONF_MAP[item.type]
  
  # Update the RRD
  RRA.convert(conf, archive, action = options.update_rrd_type, graph = item.pk)

def update_rrds():
  """
  Updates RRDs.
  """
  # We must close the database connection before we fork the worker pool, otherwise
  # resources will be shared and problems will arise!
  connection.close()
  pool = multiprocessing.Pool(processes = settings.MONITOR_GRAPH_WORKERS)
  
  try:
    pool.map(update_rrd, GraphItem.objects.all()[:])
    
    # Don't forget the global graphs
    rra_traffic = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_replicator_traffic.rrd')
    rra_status = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_nodes_by_status.rrd')
    rra_clients = os.path.join(settings.MONITOR_WORKDIR, 'rra', 'global_client_count.rrd')
    
    RRA.convert(RRALocalTraffic, rra_traffic, action = options.update_rrd_type, graph = -1)
    RRA.convert(RRANodesByStatus, rra_status, action = options.update_rrd_type, graph = -2)
    RRA.convert(RRAGlobalClients, rra_clients, action = options.update_rrd_type, graph = -3)
  except:
    logging.warning(format_exc())
  
  pool.close()
  pool.join()

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

def generate_new_node_tweet(node):
  """
  Generates a tweet when a new node connects to the network.
  """
  if not Tweet.tweets_enabled():
    return
  
  try:
    bit_api = bitly.Api(login=settings.BITLY_LOGIN, apikey=settings.BITLY_API_KEY)
    node_link = bit_api.shorten(node.get_full_url())
    msg = "A new node %s has just connected to the network %s" % (node.name, node_link)
    Tweet.post_tweet(node, msg)
  except:
    logging.warning("%s/%s: %s" % (node.name, node.ip, format_exc()))

@transaction.commit_on_success
def process_node(node_ip, ping_results, is_duped, peers, varsize_results):
  """
  Processes a single node.

  @param node_ip: Node's IP address
  @param ping_results: Results obtained from ICMP ECHO tests
  @param is_duped: True if duplicate echos received
  @param peers: Peering info from routing daemon
  @param varsize_results: Results of ICMP ECHO tests with variable payloads
  """
  transaction.set_dirty()
  
  try:
    n = Node.get_exclusive(ip = node_ip)
  except Node.DoesNotExist:
    # This might happen when we were in the middle of a renumbering and
    # did not yet have access to the node. Then after the node has been
    # renumbered we gain access, but the IP has been changed. In this
    # case we must ignore processing of this node.
    return
  
  grapher = Grapher(n)
  oldStatus = n.status
  old_last_seen = n.last_seen

  # Determine node status
  if ping_results is not None:
    n.status = NodeStatus.Up
    n.rtt_min, n.rtt_avg, n.rtt_max, n.pkt_loss = ping_results
    
    # Add RTT graph
    grapher.add_graph(GraphType.RTT, 'Latency', 'latency', n.rtt_avg, n.rtt_min, n.rtt_max)

    # Add uptime credit
    if n.uptime_last:
      n.uptime_so_far = (n.uptime_so_far or 0) + (datetime.now() - n.uptime_last).seconds
    
    n.uptime_last = datetime.now()
  else:
    n.status = NodeStatus.Visible
  
  # Measure packet loss with different packet sizes and generate a graph
  if ping_results is not None and varsize_results is not None:
    losses = [n.pkt_loss] + varsize_results
    grapher.add_graph(GraphType.PacketLoss, 'Packet Loss', 'packetloss', *losses)
  
  if is_duped:
    n.status = NodeStatus.Duped
    NodeWarning.create(n, WarningCode.DupedReplies, EventSource.Monitor)

  # Generate status change events
  if oldStatus in (NodeStatus.Down, NodeStatus.Pending, NodeStatus.New) and n.status in (NodeStatus.Up, NodeStatus.Visible):
    if oldStatus in (NodeStatus.New, NodeStatus.Pending):
      n.first_seen = datetime.now()
      if n.node_type == NodeType.Wireless:
        generate_new_node_tweet(n)

    Event.create_event(n, EventCode.NodeUp, '', EventSource.Monitor)
  elif oldStatus != NodeStatus.Duped and n.status == NodeStatus.Duped:
    Event.create_event(n, EventCode.PacketDuplication, '', EventSource.Monitor)
  
  # Add olsr peer count graph
  grapher.add_graph(GraphType.OlsrPeers, 'Routing Peers', 'olsrpeers', n.peers)

  # Add LQ/ILQ/ETX graphs
  if n.peers > 0:
    etx_avg = lq_avg = ilq_avg = 0.0
    for peer in n.get_peers():
      lq_avg += float(peer.lq)
      ilq_avg += float(peer.ilq)
      etx_avg += float(peer.etx)
    
    lq_graph = grapher.add_graph(GraphType.LQ, 'Average Link Quality', 'lq', lq_avg / n.peers, ilq_avg / n.peers)
    etx_graph = grapher.add_graph(GraphType.ETX, 'Average ETX', 'etx', etx_avg / n.peers)

    for peer in n.get_peers():
      # Link quality
      grapher.add_graph(
        GraphType.LQ,
        'Link Quality to {0}'.format(peer.dst),
        'lq_peer_{0}'.format(peer.dst.pk),
        peer.lq,
        peer.ilq,
        name = peer.dst.ip,
        parent = lq_graph
      )
      
      # ETX
      grapher.add_graph(
        GraphType.ETX,
        'ETX to {0}'.format(peer.dst),
        'etx_peer_{0}'.format(peer.dst.pk),
        peer.etx,
        name = peer.dst.ip,
        parent = etx_graph
      )

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
      
      # Treat missing firmware version file as NULL version
      if n.firmware_version == "missing":
        n.firmware_version = None
      
      # Validate BSSID and ESSID
      if n.bssid != "02:CA:FF:EE:BA:BE":
        NodeWarning.create(n, WarningCode.BSSIDMismatch, EventSource.Monitor)
      
      try:
        if n.essid != n.configured_essid:
          NodeWarning.create(n, WarningCode.ESSIDMismatch, EventSource.Monitor)
      except Project.DoesNotExist:
        pass
      
      if 'uuid' in info['general']:
        n.reported_uuid = info['general']['uuid']
        if n.reported_uuid and n.reported_uuid != n.uuid:
          NodeWarning.create(n, WarningCode.MismatchedUuid, EventSource.Monitor)

      if oldVersion != n.firmware_version:
        Event.create_event(n, EventCode.VersionChange, '', EventSource.Monitor, data = 'Old version: %s\n  New version: %s' % (oldVersion, n.firmware_version))

      if oldUptime > n.uptime:
        Event.create_event(n, EventCode.UptimeReset, '', EventSource.Monitor, data = 'Old uptime: %s\n  New uptime: %s' % (oldUptime, n.uptime))
        
        # Setup reboot mode for further graphs as we now know the node has
        # been rebooted
        grapher.enable_reboot_mode(n.uptime, old_last_seen)

      if oldChannel != n.channel and oldChannel != 0:
        Event.create_event(n, EventCode.ChannelChanged, '', EventSource.Monitor, data = 'Old channel: %s\n  New channel %s' % (oldChannel, n.channel))
      
      try:
        if n.channel != n.profile.channel:
          NodeWarning.create(n, WarningCode.ChannelMismatch, EventSource.Monitor)
      except Profile.DoesNotExist:
        pass

      if n.has_time_sync_problems():
        NodeWarning.create(n, WarningCode.TimeOutOfSync, EventSource.Monitor)

      if 'errors' in info['wifi']:
        error_count = safe_int_convert(info['wifi']['errors'])
        if error_count != n.wifi_error_count and error_count > 0:
          Event.create_event(n, EventCode.WifiErrors, '', EventSource.Monitor, data = 'Old count: %s\n  New count: %s' % (n.wifi_error_count, error_count))
        
        n.wifi_error_count = error_count
      
      if 'net' in info:
        loss_count = safe_int_convert(info['net']['losses'])
        if loss_count != n.loss_count and loss_count > 1:
          Event.create_event(n, EventCode.ConnectivityLoss, '', EventSource.Monitor, data = 'Old count: %s\n  New count: %s' % (n.loss_count, loss_count))
        
        n.loss_count = loss_count
        
        # Check VPN configuration 
        if 'vpn' in info['net']:
          n.vpn_mac = info['net']['vpn']['mac'] or None
          try:
            offset = -3
            unit = 1000
            if 'Kbit' in info['net']['vpn']['upload_limit']:
              offset = -4
              unit = 1
            
            upload_limit = safe_int_convert(info['net']['vpn']['upload_limit'][:offset]) // unit
          except TypeError:
            upload_limit = None
          
          if n.vpn_mac and n.vpn_mac != n.vpn_mac_conf:
            NodeWarning.create(n, WarningCode.VPNMacMismatch, EventSource.Monitor)
          
          try:
            if upload_limit != n.profile.vpn_egress_limit:
              NodeWarning.create(n, WarningCode.VPNLimitMismatch, EventSource.Monitor)
          except Profile.DoesNotExist:
            pass
      
      # Parse nodogsplash client information
      oldNdsStatus = n.captive_portal_status
      if 'nds' in info:
        if 'down' in info['nds'] and info['nds']['down'] == '1':
          n.captive_portal_status = False
          
          # Create a node warning when captive portal is down and the node has it
          # selected in its image generator profile
          try:
            if n.project.captive_portal and n.has_client_subnet():
              NodeWarning.create(n, WarningCode.CaptivePortalDown, EventSource.Monitor)
          except Profile.DoesNotExist:
            pass
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
      if n.has_client_subnet():
        if oldNdsStatus and not n.captive_portal_status:
          Event.create_event(n, EventCode.CaptivePortalDown, '', EventSource.Monitor)
        elif not oldNdsStatus and n.captive_portal_status:
          Event.create_event(n, EventCode.CaptivePortalUp, '', EventSource.Monitor)

      # Generate a graph for number of wifi cells
      if 'cells' in info['wifi']:
        grapher.add_graph(GraphType.WifiCells, 'Nearby WiFi Cells', 'wificells', safe_int_convert(info['wifi']['cells']) or 0)

      # Update node's MAC address on wifi iface
      if 'mac' in info['wifi']:
        n.wifi_mac = info['wifi']['mac']
      
      # Update node's RTS and fragmentation thresholds
      if 'rts' in info['wifi'] and 'frag' in info['wifi']:
        n.thresh_rts = safe_int_convert(info['wifi']['rts']) or 2347
        n.thresh_frag = safe_int_convert(info['wifi']['frag']) or 2347
      
      # Check node's multicast rate
      if 'mcast_rate' in info['wifi']:
        rate = safe_int_convert(info['wifi']['mcast_rate'])
        if rate != 5500:
          NodeWarning.create(n, WarningCode.McastRateMismatch, EventSource.Monitor)
      
      # Check node's wifi bitrate, level and noise
      if 'signal' in info['wifi']:
        bitrate = safe_int_convert(info['wifi']['bitrate'])
        signal = safe_dbm_convert(info['wifi']['signal'])
        noise = safe_dbm_convert(info['wifi']['noise'])
        snr = float(signal) - float(noise)
        
        grapher.add_graph(GraphType.WifiBitrate, 'WiFi Bitrate', 'wifibitrate', bitrate)
        grapher.add_graph(GraphType.WifiSignalNoise, 'WiFi Signal/Noise', 'wifisignalnoise', signal, noise)
        grapher.add_graph(GraphType.WifiSNR, 'WiFi Signal/Noise Ratio', 'wifisnr', snr)
      
      # Check for IP shortage
      wifi_subnet = n.subnet_set.filter(gen_iface_type = IfaceType.WiFi, allocated = True)
      if wifi_subnet and n.clients > max(0, ipcalc.Network(wifi_subnet[0].subnet, wifi_subnet[0].cidr).size() - 4):
        Event.create_event(n, EventCode.IPShortage, '', EventSource.Monitor, data = 'Subnet: %s\n  Clients: %s' % (wifi_subnet[0], n.clients))
        NodeWarning.create(n, WarningCode.IPShortage, EventSource.Monitor)
      
      # Fetch DHCP leases when available
      lease_count = 0
      if 'dhcp' in info:
        per_subnet_counts = {}
        
        for cid, client in info['dhcp'].iteritems():
          if not cid.startswith('client'):
            continue
          
          # Determine which subnet this thing belongs to
          client_subnet = n.subnet_set.ip_filter(ip_subnet__contains = client['ip'])
          if client_subnet:
            client_subnet = client_subnet[0]
            per_subnet_counts[client_subnet] = per_subnet_counts.get(client_subnet, 0) + 1
          else:
            # TODO Subnet is not announced by this node - potential problem, but ignore for now
            pass
          
          lease_count += 1
        
        # Check for IP shortage
        for client_subnet, count in per_subnet_counts.iteritems():
          if count > ipcalc.Network(client_subnet.subnet, client_subnet.cidr).size() - 4:
            Event.create_event(n, EventCode.IPShortage, '', EventSource.Monitor, data = 'Subnet: {0}\n  Leases: {1}' % (client_subnet, count))
            NodeWarning.create(n, WarningCode.IPShortage, EventSource.Monitor)
      
      # Generate a graph for number of clients
      if 'nds' in info or lease_count > 0:
        grapher.add_graph(GraphType.Clients, 'Connected Clients', 'clients', n.clients, lease_count)
      
      # Record interface traffic statistics for all interfaces
      for iid, iface in info['iface'].iteritems():
        if iid not in ('wifi0', 'wmaster0'):
          # Check mappings for known wifi interfaces so we can handle hardware changes while
          # the node is up and not generate useless intermediate graphs
          try:
            if n.profile:
              iface_wifi = n.profile.template.iface_wifi
              if Template.objects.filter(iface_wifi = iid).count() >= 1:
                iid = iface_wifi
          except Profile.DoesNotExist:
            pass
          
          grapher.add_graph(GraphType.Traffic, 'Traffic - %s' % iid, 'traffic_%s' % iid, iface['up'], iface['down'], name = iid)
      
      # Generate load average statistics
      if 'loadavg' in info['general']:
        n.loadavg_1min, n.loadavg_5min, n.loadavg_15min, n.numproc = safe_loadavg_convert(info['general']['loadavg'])
        grapher.add_graph(GraphType.LoadAverage, 'Load Average', 'loadavg', n.loadavg_1min, n.loadavg_5min, n.loadavg_15min)
        grapher.add_graph(GraphType.NumProc, 'Number of Processes', 'numproc', n.numproc)

      # Generate free memory statistics
      if 'memfree' in info['general']:
        n.memfree = safe_int_convert(info['general']['memfree'])
        buffers = safe_int_convert(info['general'].get('buffers', 0))
        cached = safe_int_convert(info['general'].get('cached', 0))
        grapher.add_graph(GraphType.MemUsage, 'Memory Usage', 'memusage', n.memfree, buffers, cached)

      # Generate solar statistics when available
      if 'solar' in info and all([x in info['solar'] for x in ('batvoltage', 'solvoltage', 'charge', 'state', 'load')]):
        states = {
          'boost'       : 1,
          'equalize'    : 2,
          'absorption'  : 3,
          'float'       : 4
        }
        
        for key, value in info['solar'].iteritems():
          if not value.strip():
            info['solar'][key] = None
        
        grapher.add_graph(GraphType.Solar, 'Solar Monitor', 'solar',
          info['solar']['batvoltage'],
          info['solar']['solvoltage'],
          info['solar']['charge'],
          states.get(info['solar']['state']),
          info['solar']['load']
        )
      
      # Generate statistics for environmental data
      if 'environment' in info:
        for key, value in info['environment'].iteritems():
          if not key.startswith('sensor'):
            continue
          if 'temp' in value:
            temp = safe_float_convert(value['temp'])
            serial = value['serial']
            grapher.add_graph(GraphType.Temperature, 'Temperature ({0})'.format(serial), 'temp_{0}'.format(serial), temp, name = serial)
      
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
      
      # Check if all selected optional packages are present in package listing
      try:
        missing_packages = []
        for package in n.profile.optional_packages.all():
          if n.installedpackage_set.filter(name = package.name).count() == 0:
            missing_packages.append(package.name)
        
        if missing_packages:
          NodeWarning.create(n, WarningCode.OptPackageNotFound, EventSource.Monitor, details = ("Packages missing: %s" % ", ".join(missing_packages)))
      except Profile.DoesNotExist:
        pass
      
      # Check if DNS works
      if 'dns' in info:
        old_dns_works = n.dns_works
        n.dns_works = info['dns']['local'] == '0' and info['dns']['remote'] == '0'
        if not n.dns_works:
          NodeWarning.create(n, WarningCode.DnsDown, EventSource.Monitor)

        if old_dns_works != n.dns_works:
          # Generate a proper event when the state changes
          if n.dns_works:
            Event.create_event(n, EventCode.DnsResolverRestored, '', EventSource.Monitor)
          else:
            Event.create_event(n, EventCode.DnsResolverFailed, '', EventSource.Monitor)
    except:
      logging.warning("Failed to interpret nodewatcher data for node '%s (%s)'!" % (n.name, n.ip))
      logging.warning(format_exc())
      NodeWarning.create(n, WarningCode.NodewatcherInterpretFailed, EventSource.Monitor)

  n.save()
  
  # When GC debugging is enabled perform some more work
  if getattr(settings, 'MONITOR_ENABLE_GC_DEBUG', None):
    gc.collect()
    return os.getpid(), len(gc.get_objects())
  
  return None, None

@transaction.commit_on_success
def check_network_status():
  """
  Performs the network status check.
  """
  # Initialize the state of nodes and subnets, remove out of date ap clients and graph items
  Node.objects.all().update(visible = False)
  Subnet.objects.all().update(visible = False)
  Link.objects.all().update(visible = False)
  APClient.objects.filter(last_update__lt = datetime.now() -  timedelta(minutes = 11)).delete()

  # Reset some states
  NodeWarning.objects.all().update(source = EventSource.Monitor, dirty = False)
  Node.objects.all().update(warnings = False, conflicting_subnets = False)

  # Fetch routing tables from OLSR
  try:
    nodes, hna = wifi_utils.get_tables(settings.MONITOR_OLSR_HOST)
  except TypeError:
    logging.error("Unable to fetch routing tables from '%s'!" % settings.MONITOR_OLSR_HOST)
    return

  # Ping nodes present in the database and visible in OLSR
  dbNodes = {}
  nodesToPing = []
  for nodeIp in nodes.keys():
    try:
      # Try to get the node from the database
      n = Node.get_exclusive(ip = nodeIp)
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
        
        # Create a warning since node is not registered
        NodeWarning.create(n, WarningCode.UnregisteredNode, EventSource.Monitor)
        n.save()
      
      dbNodes[nodeIp] = n
    except Node.DoesNotExist:
      # Node does not exist, create an invalid entry for it
      n = Node(ip = nodeIp, status = NodeStatus.Invalid, last_seen = datetime.now())
      n.visible = True
      n.node_type = NodeType.Unknown
      n.peers = len(nodes[nodeIp].links)
      
      # Check if there are any renumber notices for this IP address
      try:
        notice = RenumberNotice.objects.get(original_ip = nodeIp)
        n.status = NodeStatus.AwaitingRenumber
        n.node_type = notice.node.node_type
        n.awaiting_renumber = True
      except RenumberNotice.DoesNotExist:
        pass
      
      n.save(force_insert = True)
      dbNodes[nodeIp] = n

      # Create an event and append a warning since an unknown node has appeared
      NodeWarning.create(n, WarningCode.UnregisteredNode, EventSource.Monitor)
      Event.create_event(n, EventCode.UnknownNodeAppeared, '', EventSource.Monitor)
  
  # Add a warning to all nodes that have been stuck in renumbering state for over a week
  for node in Node.objects.filter(renumber_notices__renumbered_at__lt = datetime.now() - timedelta(days = 7)):
    NodeWarning.create(node, WarningCode.LongRenumber, EventSource.Monitor)
    node.save()
  
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
  
  # Generate timestamp and snapshot identifier
  timestamp = datetime.now()
  snapshot_id = int(time.time())
  
  # Setup all node peerings
  for nodeIp, node in nodes.iteritems():
    n = dbNodes[nodeIp]
    n.redundancy_link = False
    links = []
    
    # Find old VPN server peers
    old_vpn_peers = set([p.dst for p in n.get_peers().filter(dst__vpn_server = True)])

    for peerIp, lq, ilq, etx, vtime in node.links:
      try:
        l = Link.objects.get(src = n, dst = dbNodes[peerIp])
      except Link.DoesNotExist:
        l = Link(src = n, dst = dbNodes[peerIp])
      
      l.lq = float(lq)
      l.ilq = float(ilq)
      l.etx = float(etx)
      l.vtime = vtime
      l.visible = True
      l.save()
      links.append(l)
      
      # Check if any of the peers has never peered with us before
      if n.is_adjacency_important() and l.dst.is_adjacency_important() and not n.peer_history.filter(pk = l.dst.pk).count():
        n.peer_history.add(l.dst)
        Event.create_event(n, EventCode.AdjacencyEstablished, '', EventSource.Monitor,
                           data = 'Peer node: %s' % l.dst, aggregate = False)
        Event.create_event(l.dst, EventCode.AdjacencyEstablished, '', EventSource.Monitor,
                           data = 'Peer node: %s' % n, aggregate = False)

      # Check if we have a peering with any VPN servers
      if l.dst.vpn_server:
        n.redundancy_link = True
    
    if not n.is_invalid():
      # Determine new VPN server peers
      new_vpn_peers = set([p.dst for p in n.get_peers().filter(visible = True, dst__vpn_server = True)])
      
      if old_vpn_peers != new_vpn_peers:
        for p in old_vpn_peers:
          if p not in new_vpn_peers:
            # Redundancy loss has ocurred
            Event.create_event(n, EventCode.RedundancyLoss, '', EventSource.Monitor,
                               data = 'VPN server: %s' % p)
        
        for p in new_vpn_peers:
          if p not in old_vpn_peers:
            # Redundancy restoration has ocurred
            Event.create_event(n, EventCode.RedundancyRestored, '', EventSource.Monitor,
                               data = 'VPN server: %s' % p)
      
      # Issue a warning when node requires peering but has none
      if n.redundancy_req and not n.redundancy_link:
        NodeWarning.create(n, WarningCode.NoRedundancy, EventSource.Monitor)
    
    n.save()
    
    # Archive topology information
    data_archive.record_topology_entry(snapshot_id, timestamp, n, links)

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
      except Subnet.DoesNotExist:
        s = Subnet(node = dbNodes[nodeIp], subnet = subnet, cidr = int(cidr), last_seen = datetime.now())
        s.visible = True
        s.allocated = False
      
      # Save previous subnet status for later use
      old_status = s.status
      
      # Set status accoording to allocation flag
      if s.allocated:
        s.status = SubnetStatus.AnnouncedOk
      else:
        s.status = SubnetStatus.NotAllocated
      
      # Check if this is a more specific prefix announce for an allocated prefix
      if s.is_more_specific() and not s.allocated:
        s.status = SubnetStatus.Subset
      
      # Check if this is a hijack
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
      except Subnet.DoesNotExist:
        pass
      
      # Generate an event if status has changed
      if old_status != s.status and s.status == SubnetStatus.Hijacked:
        Event.create_event(n, EventCode.SubnetHijacked, '', EventSource.Monitor,
                           data = 'Subnet: %s/%s\n  Allocated to: %s' % (s.subnet, s.cidr, origin.node))
      
      # Flag node entry with warnings flag for unregistered announces
      if not s.is_properly_announced():
        if s.node.border_router and not s.is_from_known_pool():
          # TODO when we have peering announce registration this should first check if
          #      the subnet is registered as a peering
          s.status = SubnetStatus.Peering
        
        if not s.node.border_router or s.status == SubnetStatus.Hijacked or s.is_from_known_pool():
          # Add a warning message for unregistered announced subnets
          NodeWarning.create(s.node, WarningCode.UnregisteredAnnounce, EventSource.Monitor)
          s.node.save()
      
      s.save()
      
      # Detect subnets that cause conflicts and raise warning flags for all involved
      # nodes
      if s.is_conflicting():
        NodeWarning.create(s.node, WarningCode.AnnounceConflict, EventSource.Monitor)
        s.node.conflicting_subnets = True
        s.node.save()
        
        for cs in s.get_conflicting_subnets():
          NodeWarning.create(cs.node, WarningCode.AnnounceConflict, EventSource.Monitor)
          cs.node.conflicting_subnets = True
          cs.node.save()
  
  # Remove subnets that were hijacked but are not visible anymore
  for s in Subnet.objects.filter(status = SubnetStatus.Hijacked, visible = False):
    Event.create_event(s.node, EventCode.SubnetRestored, '', EventSource.Monitor, data = 'Subnet: %s/%s' % (s.subnet, s.cidr))
    s.delete()
  
  # Remove (or change their status) subnets that are not visible
  Subnet.objects.filter(allocated = False, visible = False).delete()
  Subnet.objects.filter(allocated = True, visible = False).update(status = SubnetStatus.NotAnnounced)
  
  for subnet in Subnet.objects.filter(status = SubnetStatus.NotAnnounced, node__visible = True):
    NodeWarning.create(subnet.node, WarningCode.OwnNotAnnounced, EventSource.Monitor)
    subnet.node.save()
  
  # Remove invisible unknown nodes
  for node in Node.objects.filter(status = NodeStatus.Invalid, visible = False).all():
    # Create an event since an unknown node has disappeared
    Event.create_event(node, EventCode.UnknownNodeDisappeared, '', EventSource.Monitor)
  
  Node.objects.filter(status__in = (NodeStatus.Invalid, NodeStatus.AwaitingRenumber), visible = False).delete()
  
  # Remove invisible links
  Link.objects.filter(visible = False).delete()
  
  # Add nodes to topology map and generate output
  if not getattr(settings, 'MONITOR_DISABLE_GRAPHS', None):
    # Only generate topology when graphing is not disabled
    topology = DotTopologyPlotter()
    for node in dbNodes.values():
      topology.addNode(node)
    topology.save(os.path.join(settings.GRAPH_DIR, 'network_topology.png'), os.path.join(settings.GRAPH_DIR, 'network_topology.dot'))

  # Ping the nodes to prepare information for later node processing
  varsize_results = {}
  results, dupes = wifi_utils.ping_hosts(10, nodesToPing)
  for packet_size in (100, 500, 1000, 1480):
    r, d = wifi_utils.ping_hosts(10, nodesToPing, packet_size - 8)
    for node_ip in nodesToPing:
      varsize_results.setdefault(node_ip, []).append(r[node_ip][3] if node_ip in r else None)
  
  if getattr(settings, 'MONITOR_DISABLE_MULTIPROCESSING', None):
    # Multiprocessing is disabled (the MONITOR_DISABLE_MULTIPROCESSING option is usually
    # used for debug purpuses where a single process is prefered)
    for node_ip in nodesToPing:
      process_node(node_ip, results.get(node_ip), node_ip in dupes, nodes[node_ip].links, varsize_results.get(node_ip))
    
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
        WORKER_POOL.apply_async(process_node, (node_ip, results.get(node_ip), node_ip in dupes, nodes[node_ip].links, varsize_results.get(node_ip)))
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
    if getattr(settings, 'MONITOR_ENABLE_GC_DEBUG', None):
      global _MAX_GC_OBJCOUNT
      objcount = sum(objects.values())
      
      if '_MAX_GC_OBJCOUNT' not in globals():
        _MAX_GC_OBJCOUNT = objcount
      
      logging.debug("GC object count: %d %s" % (objcount, "!M" if objcount > _MAX_GC_OBJCOUNT else ""))
      _MAX_GC_OBJCOUNT = max(_MAX_GC_OBJCOUNT, objcount)
  
  # Cleanup all out of date warnings
  NodeWarning.clear_obsolete_warnings(EventSource.Monitor)

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
  
  # Autodetect fping location
  FPING_LOCATIONS = [
    getattr(settings, 'FPING_BIN', None),
    '/usr/sbin/fping',
    '/usr/bin/fping',
    '/sw/sbin/fping'
  ]
  for fping_loc in FPING_LOCATIONS:
    if not fping_loc:
      continue
    if os.path.isfile(fping_loc):
      wifi_utils.FPING_BIN = fping_loc
      logging.info("Found fping in %s." % fping_loc)
      break
  else:
    print "ERROR: Failed to find fping binary! Check that it is installed properly."
    exit(1)
  
  # Autodetect graphviz location
  GRAPHVIZ_LOCATIONS = [
    getattr(settings, 'GRAPHVIZ_BIN', None),
    '/usr/bin/neato',
    '/sw/bin/neato'
  ]
  for graphviz_loc in GRAPHVIZ_LOCATIONS:
    if not graphviz_loc:
      continue
    if os.path.isfile(graphviz_loc):
      DotTopologyPlotter.GRAPHVIZ_BIN = graphviz_loc
      logging.info("Found graphviz in %s." % graphviz_loc)
      break
  else:
    print "ERROR: Failed to find graphviz binary! Check that it is installed properly."
    exit(1)

  # Check if we should just regenerate the graphs
  if options.regenerate_graphs:
    # Regenerate all graphs that need redrawing
    print ">>> Regenerating graphs from RRAs..."
    regenerate_graphs()
    print ">>> Graph generation completed."
    exit(0)
  
  # Check if we should just update RRDs
  if options.update_rrds:
    print ">>> Updating RRDs..."
    update_rrds()
    print ">>> RRD updates completed."
    exit(0)
  
  # Check if we should just perform reverse population of RRDs
  if options.reverse_populate:
    try:
      node = Node.objects.get(pk = options.rp_node)
    except Node.DoesNotExist:
      print "ERROR: Invalid node specified."
      exit(1)
    
    try:
      conf = RRA_CONF_MAP[int(options.rp_graph)]
    except (ValueError, KeyError):
      print "ERROR: Invalid graph type specified."
      exit(1)
    
    print ">>> Reverse populating RRDs for node '%s', graph '%s'..." % (node.name, conf.__name__)
    
    try:
      graph = GraphItem.objects.filter(node = node, type = int(options.rp_graph))[0]
    except IndexError:
      print "ERROR: No graph items of specified type are available for this node."
      exit(1)
    
    archive = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
    RRA.reverse_populate(node, conf, archive)
    exit(0)
  
  # Check if we should just perform stress testing
  if options.stress_test:
    print ">>> Performing stress test..."
    
    # Force some settings
    settings.MONITOR_ENABLE_SIMULATION = True
    settings.MONITOR_DISABLE_MULTIPROCESSING = True
    
    # Check network status in a tight loop
    try:
      for i in xrange(1000):
        check_network_status()
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
  if getattr(settings, 'DEBUG', None):
    logging.warning("Debug mode is enabled, monitor will leak memory!")
  
  if getattr(settings, 'MONITOR_ENABLE_SIMULATION', None):
    logging.warning("All feeds are being simulated!")
  
  if getattr(settings, 'MONITOR_DISABLE_MULTIPROCESSING', None):
    logging.warning("Multiprocessing mode disabled.")
  
  if getattr(settings, 'MONITOR_DISABLE_GRAPHS', None):
    logging.warning("Graph generation disabled.")
  
  if getattr(settings, 'MONITOR_ENABLE_GC_DEBUG', None):
    logging.warning("Garbage collection debugging enabled.")
  
  # Create worker pool and start processing
  logging.info("nodewatcher network monitoring system is initializing...")
  WORKER_POOL = multiprocessing.Pool(processes = settings.MONITOR_WORKERS)
  try:
    while True:
      # Perform all processing
      try:
        check_network_status()
        check_dead_graphs()
        check_global_statistics()
        check_events()
        
        if getattr(settings, 'MONITOR_DISABLE_GRAPHS', None):
          pass
        else:
          regenerate_graphs()
      except KeyboardInterrupt:
        raise
      except:
        logging.warning(format_exc())
      
      # Go to sleep for a while
      sleep(settings.MONITOR_POLL_INTERVAL)
  except:
    logging.warning("Terminating workers...")
    WORKER_POOL.terminate()

