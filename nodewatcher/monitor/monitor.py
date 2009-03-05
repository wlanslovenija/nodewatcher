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
from wlanlj.nodes.models import Node, NodeStatus, Subnet, SubnetStatus, APClient, Link, GraphType, GraphItem
from django.db import transaction

# Import other stuff
from lib.wifi_utils import OlsrParser, PingParser
from lib.nodewatcher import NodeWatcher
from lib.rra import RRA, RRAIface, RRAClients, RRARTT, RRALinkQuality, RRASolar
from lib.topology import DotTopologyPlotter
from time import sleep
from datetime import datetime, timedelta
from traceback import format_exc
import pwd
import logging

WORKDIR = "/home/monitor"
GRAPHDIR = "/var/www/nodes.wlan-lj.net/graphs"

@transaction.commit_manually
def main():
  while True:
    try:
      checkMeshStatus()
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

def safe_date_convert(timestamp):
  """
  A helper method for converting a string timestamp into a datetime
  object.
  """
  try:
    return datetime.fromtimestamp(int(timestamp))
  except:
    return None

def add_graph(node, name, type, conf, title, filename, *values):
  """
  A helper function for generating graphs.
  """
  rra = os.path.join(WORKDIR, 'rra', '%s.rrd' % filename)
  RRA.update(node, conf, rra, *values)
  RRA.graph(conf, title, os.path.join(GRAPHDIR, '%s.png' % filename), *[rra for i in xrange(len(values))])
  
  try:
    graph = GraphItem.objects.get(node = node, name = name, type = type)
  except GraphItem.DoesNotExist:
    graph = GraphItem(node = node, name = name, type = type)
    graph.rra = '%s.rrd' % filename
    graph.graph = '%s.png' % filename
    graph.title = title

  graph.last_update = datetime.now()
  graph.save()

def checkMeshStatus():
  """
  Performs a mesh status check.
  """
  # Remove all invalid nodes and subnets
  Node.objects.filter(status = NodeStatus.Invalid).delete()
  Subnet.objects.filter(status = SubnetStatus.NotAllocated).delete()
  APClient.objects.filter(last_update__lt = datetime.now() -  timedelta(minutes = 11)).delete()
  GraphItem.objects.filter(last_update__lt = datetime.now() - timedelta(days = 1)).delete()

  # Mark all nodes as down and all subnets as not announced
  Node.objects.filter(status__lt = NodeStatus.UserSpecifiedMark).update(status = NodeStatus.Down, warnings = False)
  Subnet.objects.update(status = SubnetStatus.NotAnnounced)
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
      n.warnings = True
      n.peers = len(nodes[nodeIp].links)
      n.save()
      dbNodes[nodeIp] = n
  
  # Setup all node peerings
  for nodeIp, node in nodes.iteritems():
    n = dbNodes[nodeIp]

    for peerIp, lq, ilq, etx in node.links:
      l = Link(src = n, dst = dbNodes[peerIp], lq = float(lq), ilq = float(ilq), etx = float(etx))
      l.save()
  
  # Add nodes to topology map and generate output
  for node in dbNodes.values():
    topology.addNode(node)

  topology.save(os.path.join(GRAPHDIR, 'mesh_topology.png'))

  # Ping the nodes and update valid node status in the database
  results, dupes = PingParser.pingHosts(10, nodesToPing)
  for nodeIp in nodesToPing:
    n = dbNodes[nodeIp]

    # Determine node status
    if nodeIp in results:
      n.status = NodeStatus.Up
      n.rtt_min, n.rtt_avg, n.rtt_max, n.pkt_loss = results[nodeIp]
      
      # Add RTT graph
      add_graph(n, '', GraphType.RTT, RRARTT, 'Latency', 'latency_%s' % nodeIp, n.rtt_avg)
    else:
      n.status = NodeStatus.Visible

    if nodeIp in dupes:
      n.status = NodeStatus.Duped
      n.warnings = True
    
    # Add LQ/ILQ graphs
    lq_avg = ilq_avg = 0.0
    for peer in nodes[nodeIp].links:
      lq_avg += float(peer[1])
      ilq_avg += float(peer[2])
    
    add_graph(n, '', GraphType.LQ, RRALinkQuality, 'Link Quality', 'lq_%s' % nodeIp, lq_avg / n.peers, ilq_avg / n.peers)

    n.last_seen = datetime.now()

    # Since the node appears to be up, let's fetch details
    info = NodeWatcher.fetch(nodeIp)
    if info:
      try:
        n.firmware_version = info['general']['version']
        n.local_time = safe_date_convert(info['general']['local_time'])
        n.bssid = info['wifi']['bssid']
        n.essid = info['wifi']['essid']
        n.channel = NodeWatcher.frequency_to_channel(info['wifi']['frequency'])
        n.clients = 0
        
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

        # Record interface traffic statistics for all interfaces
        for iid, iface in info['iface'].iteritems():
          if iid not in ('wifi0', 'wmaster0'):
            add_graph(n, iid, GraphType.Traffic, RRAIface, 'Traffic - %s' % iid, 'traffic_%s_%s' % (nodeIp, iid), iface['up'], iface['down'])

        # Generate solar statistics when available
        if 'solar' in info:
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
        s.status = SubnetStatus.AnnouncedOk
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
  os.setgid(info.pw_gid)
  os.setuid(info.pw_uid)

  # Enter main
  main()

