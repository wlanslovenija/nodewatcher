from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.template import loader, Context
from django.conf import settings
from wlanlj.nodes.locker import require_lock, model_lock
from wlanlj.nodes import ipcalc
from wlanlj.generator.types import IfaceType
from wlanlj.dns.models import Zone, Record
from datetime import datetime, timedelta
import uuid

# This will select the proper IP lookup mechanism, so it will also work on
# non-PostgreSQL databases (but it will be much slower for larger sets).
if settings.DATABASE_ENGINE.startswith('postgresql'):
  from wlanlj.nodes.util import IPField, IPManager
else:
  from wlanlj.nodes.util_dummy import IPField, IPManager

class Project(models.Model):
  """
  This class represents a project. Each project can contains some
  nodes and is also assigned a default IP allocation pool.
  """
  name = models.CharField(max_length = 50)
  description = models.CharField(max_length = 200)
  pool = models.ForeignKey('Pool')
  channel = models.IntegerField()
  ssid = models.CharField(max_length = 50)
  sticker = models.CharField(max_length = 50)
  zone = models.ForeignKey(Zone, null = True)
  
  # Geographical location
  geo_lat = models.FloatField(null = True)
  geo_long = models.FloatField(null = True)
  geo_zoom = models.IntegerField(null = True)
  
  # Additional IP allocation pools
  pools = models.ManyToManyField('Pool', related_name = 'projects')
  
  def has_geoloc(self):
    """
    Returns true if this project has geographical location defined.
    """
    return self.geo_lat and self.geo_long and self.geo_zoom
  
  def has_nodes(self):
    """
    Returns true if this project has nodes.
    """
    return self.nodes.all().count() > 0

  def __unicode__(self):
    """
    Returns this project's name.
    """
    return self.name

class AntennaType:
  """
  Valid antenna type codes.
  """
  Unknown = 0
  Omni = 1
  Sector = 2
  Directional = 3

class PolarizationType:
  """
  Valid polarization type codes.
  """
  Unknown = 0
  Horizontal = 1
  Vertical = 2
  Circular = 3

class NodeStatus:
  """
  Valid node status codes.
  """
  # Standard status codes set by the monitoring daemon
  Up = 0
  Visible = 1
  Down = 2
  Duped = 3
  Invalid = 4
  New = 5
  Pending = 6
  AwaitingRenumber = 7
  
  @staticmethod
  def as_string(status):
    """
    Returns a node's status as a human readable string.
    """
    if status == NodeStatus.Up:
      return "up"
    elif status == NodeStatus.Visible:
      return "visible"
    elif status == NodeStatus.Down:
      return "down"
    elif status == NodeStatus.Duped:
      return "duped"
    elif status == NodeStatus.Invalid:
      return "invalid"
    elif status == NodeStatus.New:
      return "new"
    elif status == NodeStatus.Pending:
      return "pending"
    elif status == NodeStatus.AwaitingRenumber:
      return "awaitingrenumber"
    else:
      return "unknown"

class NodeType:
  """
  Valid node types.
  """
  Server = 1
  Mesh = 2
  Test = 3
  Unknown = 4
  Mobile = 5

class Node(models.Model):
  """
  This class represents a single node in the mesh.
  """
  uuid = models.CharField(max_length = 40, primary_key = True)
  ip = models.CharField(max_length = 40, unique = True)
  name = models.CharField(max_length = 50, null = True, unique = True)
  owner = models.ForeignKey(User, null = True)
  location = models.CharField(max_length = 200, null = True)
  project = models.ForeignKey(Project, null = True, related_name = 'nodes')
  notes = models.CharField(max_length = 1000, null = True)
  url = models.CharField(max_length = 200, null = True)

  # System nodes are special purpuse nodes that provide external
  # services such as VPN
  system_node = models.BooleanField(default = False)
  border_router = models.BooleanField(default = False)
  node_type = models.IntegerField(default = NodeType.Mesh)
  redundancy_link = models.BooleanField(default = False)
  redundancy_req = models.BooleanField(default = False)
  conflicting_subnets = models.BooleanField(default = False)

  # Geographical location
  geo_lat = models.FloatField(null = True)
  geo_long = models.FloatField(null = True)

  # Antenna information
  ant_external = models.BooleanField(default = False)
  ant_polarization = models.IntegerField(default = PolarizationType.Unknown)
  ant_type = models.IntegerField(default = AntennaType.Unknown)
  
  # Node visibility between monitoring runs (this is only used by the monitor daemon)
  visible = models.BooleanField()

  # Basic status (set by the monitor daemon)
  warnings = models.BooleanField(default = False)
  status = models.IntegerField(null = True)
  peers = models.IntegerField(null = True, default = 0)
  peer_list = models.ManyToManyField('self', through = 'Link', symmetrical = False)
  last_seen = models.DateTimeField(null = True)
  first_seen = models.DateTimeField(null = True)
  channel = models.IntegerField(null = True)
  wifi_mac = models.CharField(max_length = 20, null = True)
  vpn_mac = models.CharField(max_length = 20, null = True)
  vpn_mac_conf = models.CharField(max_length = 20, null = True, unique = True)
  awaiting_renumber = models.BooleanField(default = False)

  # RTT measurements (set by the monitor daemon)
  rtt_min = models.FloatField(null = True)
  rtt_avg = models.FloatField(null = True)
  rtt_max = models.FloatField(null = True)
  pkt_loss = models.IntegerField(null = True)

  # Aditional status (set by the monitor daemon)
  firmware_version = models.CharField(max_length = 50, null = True)
  bssid = models.CharField(max_length = 50, null = True)
  essid = models.CharField(max_length = 50, null = True)
  local_time = models.DateTimeField(null = True)
  clients = models.IntegerField(null = True)
  clients_so_far = models.IntegerField(default = 0)
  uptime = models.IntegerField(null = True)
  uptime_so_far = models.IntegerField(null = True)
  uptime_last = models.DateTimeField(null = True)
  loadavg_1min = models.FloatField(null = True)
  loadavg_5min = models.FloatField(null = True)
  loadavg_15min = models.FloatField(null = True)
  memfree = models.IntegerField(null = True)
  numproc = models.IntegerField(null = True)
  captive_portal_status = models.BooleanField(default = True)
  dns_works = models.BooleanField(default = True)
  reported_uuid = models.CharField(max_length = 40, null = True)
  thresh_rts = models.IntegerField(null = True)
  thresh_frag = models.IntegerField(null = True)
  
  def reset(self):
    """
    Resets node data.
    """
    self.status = NodeStatus.Pending
    self.last_seen = None
    self.first_seen = None
    self.channel = None
    self.wifi_mac = None
    self.vpn_mac = None
    self.rtt_min = None
    self.rtt_avg = None
    self.rtt_max = None
    self.pkt_loss = None
    self.firmware_version = None
    self.bssid = None
    self.essid = None
    self.local_time = None
    self.clients = 0
    self.clients_so_far = 0
    self.uptime = None
    self.uptime_so_far = None
    self.loadavg_1min = None
    self.loadavg_5min = None
    self.loadavg_15min = None
    self.memfree = None
    self.numproc = None
    self.captive_portal_status = True
    self.thresh_rts = None
    self.thresh_frag = None

    # Mark related graph items for removal by the monitoring daemon
    self.graphitem_set.all().update(need_removal = True)
    GraphItem.objects.filter(type = GraphType.LQ, name = self.ip).update(need_removal = True)
  
  def rename_graphs(self, graph_type, old, new):
    """
    Renames node's graph items (changes their unique name).
    
    @param graph_type: Only rename items of this type
    @param old: Old name
    @param new: New name
    """
    if old == new:
      return
    
    self.graphitem_set.filter(type = graph_type, name = new).delete()
    self.graphitem_set.filter(type = graph_type, name = old).update(name = new)
  
  def has_time_sync_problems(self):
    """
    Returns true if local and server clocks are too far apart.
    """
    return self.local_time and abs(datetime.now() - self.local_time).seconds > 1800

  def should_draw_on_map(self):
    """
    Returns true if this node should be visible on the map.
    """
    return not self.system_node and self.geo_lat and self.geo_long
  
  def get_graphs(self):
    """
    Returns a list of traffic graph items.
    """
    return self.graphitem_set.filter(parent = None).order_by('-type', 'name')

  def is_down(self):
    """
    Returns true if the node is currently down.
    """
    return self.status not in (NodeStatus.Up, NodeStatus.Duped)

  def is_resettable(self):
    """
    Returns true if the node can be reset.
    """
    return self.status in (NodeStatus.Down, NodeStatus.Pending)
  
  def is_pending(self):
    """
    Returns true if the node hasn't yet been seen on the network.
    """
    return self.status in (NodeStatus.Pending, NodeStatus.New)
  
  def is_invalid(self):
    """
    Returns true if the node is invalid.
    """
    return self.status in (NodeStatus.Invalid, NodeStatus.AwaitingRenumber)

  def is_mesh_node(self):
    """
    Returns true if the node is a mesh node.
    """
    return self.node_type in (NodeType.Mesh, NodeType.Test)

  def is_mobile_node(self):
    """
    Returns true if the node is a mobile node.
    """
    return self.node_type == NodeType.Mobile
  
  def get_primary_ip_pool(self):
    """
    Returns the pool the primary IP is located in.
    """
    try:
      return Pool.objects.ip_filter(ip_subnet__contains = "%s/32" % self.ip).get(parent = None)
    except Pool.DoesNotExist:
      return None
  
  def is_primary_ip_in_subnet(self):
    """
    Returns true if node's primary IP is allocated to this node in a subnet.
    """
    return self.subnet_set.ip_filter(ip_subnet__contains = "%s/32" % self.ip).filter(allocated = True).exclude(cidr = 0).count() > 0
  
  def get_renumbered_ip(self):
    """
    Returns node's new IP address (if it has recently been renumbered).
    """
    if self.status == NodeStatus.AwaitingRenumber:
      try:
        return RenumberNotice.objects.get(original_ip = self.ip).node.ip
      except RenumberNotice.DoesNotExist:
        return _("unknown")
    else:
      return self.ip
  
  def is_max_frag_threshold(self):
    """
    Returns true if fragmentation threshold is currently at its maximum value.
    """
    return self.thresh_frag is not None and self.thresh_frag >= 2347

  def is_max_rts_threshold(self):
    """
    Returns true if RTS threshold is currently at its maximum value.
    """
    return self.thresh_rts is not None and self.thresh_rts >= 2347

  def get_original_ip(self):
    """
    Returns node's old IP address (if it has recently been renumbered).
    """
    if self.status == NodeStatus.AwaitingRenumber:
      return self.ip
    else:
      return self.renumber_notices.all()[0].original_ip
  
  def node_type_as_string(self):
    """
    Returns node type as string.
    """
    if self.node_type == NodeType.Mesh:
      return _("Mesh node")
    elif self.node_type == NodeType.Server:
      return _("Server node")
    elif self.node_type == NodeType.Test:
      return _("Test node")
    elif self.node_type == NodeType.Mobile:
      return _("Mobile node")
    else:
      return _("unknown node")

  def node_type_as_string_plural(self):
    """
    Returns node type as string.
    """
    if self.node_type == NodeType.Mesh:
      return _("Mesh nodes")
    elif self.node_type == NodeType.Server:
      return _("Server nodes")
    elif self.node_type == NodeType.Test:
      return _("Test nodes")
    elif self.node_type == NodeType.Mobile:
      return _("Mobile nodes")
    else:
      return _("unknown nodes")

  def get_warnings(self):
    """
    Returns a list of warnings for this node.
    """
    w = []
    if self.status == NodeStatus.Invalid:
      w.append(_("Node is not registered in the node database!"))

    if self.status == NodeStatus.Duped:
      w.append(_("Monitor has received duplicate ICMP ECHO packets!"))

    if self.subnet_set.filter(status = SubnetStatus.NotAllocated) and not self.border_router:
      w.append(_("Node is announcing subnets that are not allocated to it!"))

    if self.subnet_set.filter(status = SubnetStatus.NotAnnounced) and not self.is_down():
      w.append(_("Node is not announcing its own allocated subnets!"))

    if self.has_time_sync_problems() and not self.is_down():
      w.append(_("Node's local clock is more than 30 minutes out of sync!"))

    if self.redundancy_req and not self.redundancy_link:
      w.append(_("Node requires direct border gateway peering but has none!"))

    if not self.captive_portal_status and not self.is_down():
      w.append(_("Captive portal daemon is down!"))

    if not self.dns_works and not self.is_down():
      w.append(_("Node's DNS resolver does not respond!"))
    
    if self.conflicting_subnets:
      w.append(_("Node is announcing or has allocated one or more subnets that are in conflict with other nodes! Please check subnet listing and investigate why the problem is ocurring!"))
    
    if self.reported_uuid and self.reported_uuid != self.uuid:
      w.append(_("Reported node UUID does not match this node! This might indicate a node/firmware mismatch."))

    return w
  
  def get_stability(self):
    """
    Returns this node's stability factor.
    """
    if not self.first_seen or not self.uptime_so_far:
      return None

    dt = abs(self.first_seen - datetime.now())
    return "%.02f" % (float(self.uptime_so_far) / (dt.days*3600*24 + dt.seconds) * 100)

  def has_allocated_subnets(self, type = IfaceType.WiFi):
    """
    Returns true if node has subnets allocated to the specified interface.
    """
    if self.subnet_set.filter(allocated = True, gen_iface_type = type):
      return True

    return False
  
  def get_subnets(self):
    """
    Returns properly ordered subnets.
    """
    return self.subnet_set.all().order_by("ip_subnet")
  
  def get_peers(self):
    """
    Returns properly ordered peers.
    """
    return self.src.all().order_by("dst__name")

  def ant_type_as_string(self):
    """
    Returns this node's antenna type as a string.
    """
    if self.ant_type == AntennaType.Omni:
      return _("Omni")
    elif self.ant_type == AntennaType.Sector:
      return _("Sector")
    elif self.ant_type == AntennaType.Directional:
      return _("Directional")
    else:
      return _("unknown")

  def ant_polarization_as_string(self):
    """
    Returns this node's antenna polarization as a string.
    """
    if self.ant_polarization == PolarizationType.Horizontal:
      return _("Horizontal")
    elif self.ant_polarization == PolarizationType.Vertical:
      return _("Vertical")
    elif self.ant_polarization == PolarizationType.Circular:
      return _("Circular")
    else:
      return _("unknown")

  def status_as_string(self):
    """
    Returns this node's status as a human readable string.
    """
    return NodeStatus.as_string(self.status)
  
  def ensure_exclusive_access(self):
    """
    Locks this model instance for update until end of transaction.
    """
    model_lock(self)
  
  @staticmethod
  def get_exclusive(**kwargs):
    """
    Returns an object with exclusive access.
    """
    n = Node.objects.get(**kwargs)
    n.ensure_exclusive_access()
    return Node.objects.get(**kwargs)
  
  def save(self, **kwargs):
    """
    Override save so we can generate UUIDs.
    """
    if not self.uuid:
      self.pk = str(uuid.uuid4())
    
    super(Node, self).save(**kwargs)
  
  def __unicode__(self):
    """
    Returns a string representation of this node.
    """
    if not self.name:
      return "unknown (%s)" % self.ip

    return "%s (%s)" % (self.name, self.ip)

class Link(models.Model):
  """
  This class represents a peering relationship between nodes.
  """
  src = models.ForeignKey(Node, related_name = 'src')
  dst = models.ForeignKey(Node, related_name = 'dst')
  lq = models.FloatField()
  ilq = models.FloatField()
  etx = models.FloatField()

  def should_draw_on_map(self):
    """
    Returns true if this link should be visible on the map.
    """
    return self.src.should_draw_on_map() and self.dst.should_draw_on_map()

  def color(self):
    """
    Returns link's color.
    """
    if self.etx >= 1.0 and self.etx <= 2.0:
      return "#00ff00"
    elif self.etx > 2.0 and self.etx <= 5.0:
      return "#0000ff"
    else:
      return "#ff0000"

class SubnetStatus:
  """
  Subnet status codes.
  """
  AnnouncedOk = 0
  NotAllocated = 1
  NotAnnounced = 2
  Hijacked = 3
  Subset = 4

class Subnet(models.Model):
  """
  This class represents a subnet allocated to a specific node in the
  wifi mesh.
  """
  node = models.ForeignKey(Node)
  subnet = models.CharField(max_length = 40)
  cidr = models.IntegerField()
  description = models.CharField(max_length = 200, null = True)
  allocated = models.BooleanField(default = False)
  allocated_at = models.DateTimeField(null = True)

  # Basic status (set by the monitor daemon)
  visible = models.BooleanField()
  status = models.IntegerField()
  last_seen = models.DateTimeField(null = True)

  # Generator attributes
  gen_iface_type = models.IntegerField(default = IfaceType.WiFi)
  gen_dhcp = models.BooleanField(default = True)
  
  # Field for indexed lookups
  ip_subnet = IPField(null = True)
  
  # Custom manager
  objects = IPManager()
  
  def save(self, **kwargs):
    """
    Saves the model.
    """
    self.ip_subnet = '%s/%s' % (self.subnet, self.cidr)
    super(Subnet, self).save(**kwargs)
  
  def is_wifi(self):
    """
    Returns true if this subnet is a wireless one.
    """
    return self.gen_iface_type == IfaceType.WiFi
  
  def is_primary(self):
    """
    Returns true if this subnet contains the primary router identifier.
    """
    net = ipcalc.Network(self.subnet, self.cidr)
    return ipcalc.Network(self.node.ip, 32) in net 
  
  def is_conflicting(self):
    """
    Returns true if this subnet is conflicting with anouther announced
    subnet.
    """
    if self.cidr == 0:
      return False

    return Subnet.objects.ip_filter(ip_subnet__conflicts = self.ip_subnet).exclude(cidr = 0).exclude(node = self.node).count() > 0
  
  def is_announced(self):
    """
    Returns true if this subnet is being currently announced.
    """
    return self.status in (SubnetStatus.AnnouncedOk, SubnetStatus.NotAllocated, SubnetStatus.Hijacked, SubnetStatus.Subset)
  
  def is_properly_announced(self):
    """
    Returns true if this subnet is properly announced.
    """
    return self.status in (SubnetStatus.AnnouncedOk, SubnetStatus.Subset)
  
  def get_conflicting_subnets(self):
    """
    Returns conflicting subnets (if any).
    """
    if self.cidr == 0:
      return Subnet.objects.none()

    return Subnet.objects.ip_filter(ip_subnet__conflicts = self.ip_subnet).exclude(cidr = 0).exclude(node = self.node).order_by("ip_subnet")

  @staticmethod
  def is_allocated(network, cidr, exclude_node = None):
    """
    Returns true if a node has the specified subnet allocated.
    """
    overlaps = Subnet.objects.ip_filter(ip_subnet__conflicts = '%s/%s' % (network, cidr)).exclude(cidr = 0)
    if overlaps.filter(allocated = True).count() > 0:
      return True
    
    if overlaps.filter(status = SubnetStatus.Subset).count() > 0:
      return True
    
    if cidr == 32 and Node.objects.filter(ip = network).exclude(pk = exclude_node.pk if exclude_node else '').count() > 0:
      return True
    
    return False

  def status_as_string(self):
    """
    Return subnet's status as a string.
    """
    if self.status == SubnetStatus.AnnouncedOk:
      return "ok"
    elif self.status == SubnetStatus.NotAllocated:
      return "not allocated"
    elif self.status == SubnetStatus.NotAnnounced:
      return "not announced"
    elif self.status == SubnetStatus.Hijacked:
      return "collision"
    elif self.status == SubnetStatus.Subset:
      return "ok"
    else:
      return "unknown"
  
  def __unicode__(self):
    """
    Returns a string representation of this subnet.
    """
    return u"%s/%d" % (self.subnet, self.cidr)

class RenumberNotice(models.Model):
  """
  This model is used for taking note of what nodes are still pending to be
  renumbered and contains backlinks, so nodes pending renumbering don't get
  Invalid status.
  """
  node = models.ForeignKey(Node, unique = True, related_name = 'renumber_notices')
  original_ip = models.CharField(max_length = 40)
  renumbered_at = models.DateTimeField()

class APClient(models.Model):
  """
  This class represents an end-user client connected to one of the AP nodes
  being tracked via the captive portal.
  """
  node = models.ForeignKey(Node)
  ip = models.CharField(max_length = 40)
  connected_at = models.DateTimeField(null = True)
  last_update = models.DateTimeField(null = True)

  # Transfer statistics (set by the monitor daemon)
  uploaded = models.IntegerField()
  downloaded = models.IntegerField()

class GraphType:
  """
  A list of valid graph types. When adding a graph type that will
  be used by a persistent model here, you MUST update RRA_CONF_MAP
  in monitoring daemon! Otherwise the monitoring daemon will break.
  """
  Traffic = 10
  Clients = 20
  RTT = 2
  LQ = 3
  Solar = 30
  LoadAverage = 1
  MemUsage = 0
  NumProc = -1
  WifiCells = 7
  OlsrPeers = 5
  GatewayTraffic = 40

  # Global graphs
  NodesByStatus = 1000

  @staticmethod
  def as_string(type):
    """
    Returns the graph type as a human readable string.
    
    @param type: A valid graph type number
    """
    if type == GraphType.Traffic:
      return "traffic"
    elif type == GraphType.Clients:
      return "clients"
    elif type == GraphType.RTT:
      return "rtt"
    elif type == GraphType.LQ:
      return "lq"
    elif type == GraphType.Solar:
      return "solar"
    elif type == GraphType.LoadAverage:
      return "loadavg"
    elif type == GraphType.MemUsage:
      return "memusage"
    elif type == GraphType.NumProc:
      return "numproc"
    elif type == GraphType.WifiCells:
      return "wificells"
    elif type == GraphType.OlsrPeers:
      return "olsrpeers"
    elif type == GraphType.GatewayTraffic:
      return "gwtraffic"
    elif type == GraphType.NodesByStatus:
      return "nodesbystatus"
    else:
      return "unknown"

class GraphItemNP(object):
  """
  A non-persistent graph item with methods for its rendering.
  """
  node = None
  parent = None
  type = None
  name = None
  rra = None
  graph = None
  title = None
  last_update = None
  dead = False

  def __init__(self, id, type, graph, title):
    """
    Class constructor.
    
    @param id: Unique identifier
    @param type: Graph type
    @param graph: Graph image filename
    @param title: Graph title
    """
    self.id = id
    self.type = type
    self.graph = graph
    self.title = title

  def get_timespans(self):
    """
    Returns a list of graph image prefixes for different time
    periods.
    """
    return [prefix for  prefix, _ in settings.GRAPH_TIMESPANS]

  def get_children(self):
    """
    Returns properly sorted graph item children.
    """
    if not self.children:
      return []

    return self.children.order_by('-type', 'name')

  def render(self):
    """
    Renders the surrounding HTML (uses a custom template if one is
    available).
    """
    t = loader.get_template('graphs/%s.html' % GraphType.as_string(self.type))
    c = Context({
      'graph'  : self
    })

    return t.render(c)

  def type_as_string(self):
    """
    Return this graph's type as a string.
    """
    return GraphType.as_string(self.type)

class GraphItem(models.Model, GraphItemNP):
  """
  This class represents a graph of some node's parameter.
  """
  node = models.ForeignKey(Node)
  parent = models.ForeignKey('self', null = True, related_name = 'children')
  type = models.IntegerField()
  name = models.CharField(max_length = 50)
  rra = models.CharField(max_length = 200)
  graph = models.CharField(max_length = 200)
  title = models.CharField(max_length = 50)
  last_update = models.DateTimeField(null = True)
  dead = models.BooleanField(default = False)
  need_redraw = models.BooleanField(default = False)
  need_removal = models.BooleanField(default = False)

class WhitelistItem(models.Model):
  """
  This class represents a whitelisted MAC address.
  """
  owner = models.ForeignKey(User)
  mac = models.CharField(max_length = 50)
  registred_at = models.DateTimeField()
  description = models.CharField(max_length = 200, default = '')

class PoolAllocationError(Exception):
  pass

class PoolFamily:
  """
  Possible address families.
  """
  Ipv4 = 4
  Ipv6 = 6

class PoolStatus:
  """
  Possible pools states.
  """
  Free = 0
  Full = 1
  Partial = 2

class Pool(models.Model):
  """
  This class represents an IP pool - that is a subnet available for
  allocation purpuses. Every IP block that is allocated is represented
  as a Pool instance with proper parent pool reference.
  """
  parent = models.ForeignKey('self', null = True, related_name = 'children')
  family = models.IntegerField(default = 4)
  network = models.CharField(max_length = 50)
  cidr = models.IntegerField()
  status = models.IntegerField(default = PoolStatus.Free)
  description = models.CharField(max_length = 200, null = True)
  default_prefix_len = models.IntegerField(null = True)
  min_prefix_len = models.IntegerField(default = 24, null = True)
  max_prefix_len = models.IntegerField(default = 28, null = True)
  
  # Field for indexed lookups
  ip_subnet = IPField(null = True)
  
  # Custom manager
  objects = IPManager()
  
  def save(self, **kwargs):
    """
    Saves the model.
    """
    self.ip_subnet = '%s/%s' % (self.network, self.cidr)
    super(Pool, self).save(**kwargs)
  
  def split(self):
    """
    Splits this pool into two subpools.
    """
    net = ipcalc.Network(self.network, self.cidr)
    net0 = "%s/%d" % (self.network, self.cidr + 1)
    net1 = str(ipcalc.Network(long(net) + ipcalc.Network(net0).size())) 
    
    left = Pool(parent = self, family = self.family, network = self.network, cidr = self.cidr + 1)
    right = Pool(parent = self, family = self.family, network = net1, cidr = self.cidr + 1)
    left.save()
    right.save()
    
    self.status = PoolStatus.Partial
    self.save()
    
    return left, right
  
  def reserve_subnet(self, network, prefix_len, check_only = False):
    """
    Attempts to reserve a specific subnet in the allocation pool. The subnet
    must be a valid subnet and must be allocatable.
    
    @param network: Subnet address
    @param prefix_len: Subnet prefix length
    @param check_only: Should only a check be performed and no actual allocation
    """
    if not self.parent and (prefix_len < self.min_prefix_len or prefix_len > self.max_prefix_len):
      return None 
    
    net = ipcalc.Network(self.network, self.cidr)
    if ipcalc.Network(network, prefix_len) not in net:
      # We don't contain this network, so there is nothing to be done
      return None
    
    if network == self.network and self.cidr == prefix_len and self.status == PoolStatus.Free:
      # We are the network, mark as full and save
      if not check_only:
        self.status = PoolStatus.Full
        self.save()
        return self
      else:
        return True
    
    # Find the proper network between our children
    alloc = None
    if self.children.count() > 0:
      for child in self.children.exclude(status = PoolStatus.Full):
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = PoolStatus.Full).count() == 2 and not check_only:
        self.status = PoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves
      for child in self.split():
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      
      if not alloc or check_only:
        # Nothing has been allocated, this means that the given subnet
        # was invalid. Remove all children and become free again.
        self.children.all().delete()
        self.status = PoolStatus.Free
        self.save()
    
    return alloc
  
  def allocate_buddy(self, prefix_len):
    """
    Allocate IP addresses from the pool in a buddy-like allocation scheme. This
    operation may split existing free pools into smaller ones to accomodate the
    new allocation.
    
    @param prefix_len: Wanted prefix length
    """
    if self.cidr > prefix_len:
      # We have gone too far, allocation has failed
      return None
    
    if prefix_len == self.cidr and self.status == PoolStatus.Free:
      # We have found a free pool of the proper size, use it
      self.status = PoolStatus.Full
      self.save()
      return self
    
    # Pool not found, check if we have children - if we don't we'll have to split
    # and traverse the left one
    alloc = None
    if self.children.count() > 0:
      for child in self.children.exclude(status = PoolStatus.Full).order_by("ip_subnet"):
        alloc = child.allocate_buddy(prefix_len)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = PoolStatus.Full).count() == 2:
        self.status = PoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves and traverse the left half
      left, right = self.split()
      alloc = left.allocate_buddy(prefix_len)
    
    return alloc
  
  def reclaim_pools(self):
    """
    Coalesces free children back into one if possible.
    """
    if self.status == PoolStatus.Free:
      return self.parent.reclaim_pools() if self.parent else None
    
    # When all children are free, we don't need them anymore; when only some
    # are free, we mark this pool as partially free
    free_children = self.children.filter(status = PoolStatus.Free).count()
    if  free_children == 2:
      self.children.all().delete()
      self.status = PoolStatus.Free
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    elif free_children == 1:
      self.status = PoolStatus.Partial
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    else:
      # If any of the children are partial, we are partial as well
      if self.children.filter(status = PoolStatus.Partial).count() > 0:
        self.status = PoolStatus.Partial
        self.save()
        return self.parent.reclaim_pools() if self.parent else None 

  def is_leaf(self):
    """
    Returns true if this pool has no children.
    """
    return self.children.all().count() == 0

  @staticmethod
  def contains_network(network, cidr):
    """
    Returns true if any pools contain this network.
    """
    return Pool.objects.ip_filter(ip_subnet__conflicts = "%s/%s" % (network, cidr)).count() > 0
  
  def family_as_string(self):
    """
    Returns this pool's address family as a string.
    """
    if self.family == PoolFamily.Ipv4:
      return "IPv4"
    elif self.family == PoolFamily.Ipv6:
      return "IPv6"
    else:
      return _("unknown")

  def __unicode__(self):
    """
    Returns a string representation of this pool.
    """
    if self.description:
      return u"%s [%s/%d]" % (self.description, self.network, self.cidr)
    else: 
      return u"%s/%d" % (self.network, self.cidr)
  
  @require_lock('nodes_pool', 'nodes_subnet')
  def allocate_subnet(self, prefix_len = None):
    """
    Attempts to allocate a subnet from this pool.

    @param prefix_len: Wanted prefix length
    @return: A valid Pool instance of the allocated subpool
    """
    if not prefix_len:
      prefix_len = self.default_prefix_len
    
    if prefix_len < self.min_prefix_len or prefix_len > self.max_prefix_len:
      return None
    
    pool = self.allocate_buddy(prefix_len)
    return pool

class StatsSolar(models.Model):
  """
  Solar dataset storage.
  """
  node = models.ForeignKey(Node)
  timestamp = models.DateTimeField()
  batvoltage = models.FloatField()
  solvoltage = models.FloatField()
  charge = models.FloatField()
  load = models.FloatField()
  state = models.IntegerField()

class EventSource:
  """
  Valid event source identifiers.
  """
  Monitor = 1
  UserReport = 2
  NodeDatabase = 3

class EventCode:
  """
  Valid event code identifiers.
  """
  NodeDown = 1
  NodeUp = 2
  UptimeReset = 3
  InvalidSubnetAnnounce = 4
  PacketDuplication = 5
  IPShortage = 6
  ChannelChanged = 7
  RedundancyLoss = 8
  VersionChange = 9
  CaptivePortalDown = 10
  CaptivePortalUp = 11
  SubnetHijacked = 12
  SubnetRestored = 13
  DnsResolverFailed = 14
  DnsResolverRestored = 15
  RedundancyRestored = 16
  UnknownNodeAppeared = 17
  UnknownNodeDisappeared = 18

  NodeAdded = 100
  NodeRenamed = 101
  NodeRemoved = 102
  NodeRenumbered = 103

  @staticmethod
  def to_string(code):
    """
    A helper method for transforming an event code to a human
    readable string.

    @param code: A valid event code
    """
    if code == EventCode.NodeDown:
      return _("Node has gone down")
    elif code == EventCode.NodeUp:
      return _("Node has come up")
    elif code == EventCode.UptimeReset:
      return _("Node has been rebooted")
    elif code == EventCode.InvalidSubnetAnnounce:
      return _("Node is announcing invalid subnets")
    elif code == EventCode.PacketDuplication:
      return _("Duplicate ICMP ECHO replies received")
    elif code == EventCode.IPShortage:
      return _("IP shortage for wireless clients")
    elif code == EventCode.ChannelChanged:
      return _("WiFi channel has changed")
    elif code == EventCode.RedundancyLoss:
      return _("Redundant link to border gateway has gone down")
    elif code == EventCode.RedundancyRestored:
      return _("Redundant link to border gateway has been restored")
    elif code == EventCode.VersionChange:
      return _("Firmware version has changed")
    elif code == EventCode.CaptivePortalDown:
      return _("Captive portal has failed")
    elif code == EventCode.CaptivePortalUp:
      return _("Captive portal has been restored")
    elif code == EventCode.NodeAdded:
      return _("A new node has been registered")
    elif code == EventCode.SubnetHijacked:
      return _("Node is causing a subnet collision")
    elif code == EventCode.SubnetRestored:
      return _("Subnet collision is no longer present")
    elif code == EventCode.DnsResolverFailed:
      return _("DNS resolver has failed")
    elif code == EventCode.DnsResolverRestored:
      return _("DNS resolver restored")
    elif code == EventCode.NodeRenamed:
      return _("Node has been renamed")
    elif code == EventCode.NodeRemoved:
      return _("Node has been removed")
    elif code == EventCode.UnknownNodeAppeared:
      return _("Unknown node has appeared")
    elif code == EventCode.UnknownNodeDisappeared:
      return _("Unknown node is no longer visible")
    elif code == EventCode.NodeRenumbered:
      return _("Node has been renumbered")
    else:
      return _("Unknown event")


class Event(models.Model):
  """
  Event model.
  """
  timestamp = models.DateTimeField()
  node = models.ForeignKey(Node)
  code = models.IntegerField()
  summary = models.CharField(max_length = 100)
  data = models.CharField(max_length = 1000)
  source = models.IntegerField()
  counter = models.IntegerField(default = 1)
  need_resend = models.BooleanField(default = False)

  def code_to_string(self):
    """
    Converts an event code to a human readable string.
    """
    return EventCode.to_string(self.code)

  def source_to_string(self):
    """
    Converts a source identifier to a string.
    """
    if self.source == EventSource.Monitor:
      return _("Monitor")
    elif self.source == EventSource.UserReport:
      return _("User report")
    elif self.source == EventSource.NodeDatabase:
      return _("Node database")
    else:
      return _("unknown source")
  
  def should_show_link(self):
    """
    Returns true if a link to event-generating node should be added
    to the notification message.
    """
    return self.code != EventCode.NodeRemoved

  @staticmethod
  def create_event(node, code, summary, source, data = ""):
    """
    Creates a new event.
    """
    # Check if this event should be supressed because it has already
    # occurred a short while ago
    events = Event.objects.filter(node = node, code = code, timestamp__gt = datetime.now() - timedelta(minutes = 30))
    if len(events) and code not in (EventCode.NodeRenamed,):
      event = events[0]
      event.counter += 1
      event.need_resend = True
      event.save()
      return

    # Create an event instance
    event = Event(node = node)
    event.code = code
    event.summary = summary
    event.source = source
    event.data = data
    event.timestamp = datetime.now()
    event.save()
    event.post_event()

    # Check if there are any repeated events that need sending
    Event.post_events_that_need_resend()
  
  @staticmethod
  def post_events_that_need_resend():
    """
    Posts all events that need to be resent.
    """
    for event in Event.objects.filter(need_resend = True, timestamp__lt = datetime.now() - timedelta(minutes = 30)):
      event.need_resend = False
      event.save()
      event.post_event()

  def has_repeated(self):
    """
    Returns true if this event has repeated in 30 minutes from its creation.
    """
    return self.counter > 1
  
  def post_event(self):
    """
    Posts an event to all subscribers.
    """
    # Check subscriptions and post notifications
    subscriptions = EventSubscription.objects.filter(
      # Filter by nodes
      models.Q(type = SubscriptionType.SingleNode, node = self.node) | \
      models.Q(type = SubscriptionType.AllNodes) | \
      models.Q(type = SubscriptionType.MyNodes, user = self.node.owner),
      
      # Filter by event code
      models.Q(code = self.code) | models.Q(code__isnull = True)
    )

    for subscription in subscriptions:
      subscription.notify(self)

class SubscriptionType:
  """
  Valid subscription types.
  """
  SingleNode = 1
  AllNodes = 2
  MyNodes = 3

  @staticmethod
  def to_string(type):
    """
    Converts a subscription type to a human readable string.

    @param type: A valid subscription type
    """
    if type == SubscriptionType.SingleNode:
      return _("single node")
    elif type == SubscriptionType.AllNodes:
      return _("any node")
    elif type == SubscriptionType.MyNodes:
      return _("my nodes")
    else:
      return _("unknown")

class EventSubscription(models.Model):
  """
  Event subscription model.
  """
  user = models.ForeignKey(User)
  node = models.ForeignKey(Node, null = True)
  active = models.BooleanField(default = True)
  code = models.IntegerField(null = True)
  type = models.IntegerField(default = SubscriptionType.SingleNode)

  def code_to_string(self):
    """
    Converts an event code to a human readable string.
    """
    return EventCode.to_string(self.code)

  def type_to_string(self):
    """
    Converts a subscription type to a human readable string.
    """
    return SubscriptionType.to_string(self.type)
  
  def is_single_node(self):
    """
    Returns true if this subscription is for a single node.
    """
    return self.type == SubscriptionType.SingleNode

  def notify(self, event):
    """
    Notify a user about an event.

    @param event: A valid Event instance
    """
    t = loader.get_template('nodes/event_mail.txt')
    c = Context({
      'user'  : self.user,
      'event' : event
    })

    # Format node name and IP
    if event.node.name:
      name_ip = '%s/%s' % (event.node.ip, event.node.name)
    else:
      name_ip = event.node.ip

    send_mail(
      '[wlan-lj] %s - %s' % (name_ip, event.code_to_string()),
      t.render(c),
      'events@wlan-lj.net',
      [self.user.email],
      fail_silently = True
    )

class InstalledPackage(models.Model):
  """
  This model represents an installed package reported via nodewatcher.
  """
  node = models.ForeignKey(Node)
  name = models.CharField(max_length = 100)
  version = models.CharField(max_length = 50)
  last_update = models.DateTimeField()

def subnet_on_delete_callback(sender, **kwargs):
  """
  On delete callback for Subnets.
  """
  instance = kwargs['instance']
  if not instance.allocated:
    return

  try:
    subnet = Pool.objects.get(network = instance.subnet, cidr = instance.cidr)
    if subnet.status == PoolStatus.Full:
      subnet.status = PoolStatus.Free
      subnet.save()
      subnet.reclaim_pools()
  except Pool.DoesNotExist:
    pass

def node_on_delete_callback(sender, **kwargs):
  """
  On delete callback for Nodes.
  """
  Record.remove_for_node(kwargs['instance'])

  # Check if node has a /32 subnet assigned and free it if needed
  try:
    subnet = Pool.objects.get(network = kwargs['instance'].ip, cidr = 32)
    if subnet.status == PoolStatus.Full:
      subnet.status = PoolStatus.Free
      subnet.save()
      subnet.reclaim_pools()
  except Pool.DoesNotExist:
    pass

models.signals.pre_delete.connect(subnet_on_delete_callback, sender = Subnet)
models.signals.pre_delete.connect(node_on_delete_callback, sender = Node)

