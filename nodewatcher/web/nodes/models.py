from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.template import loader, Context
from django.conf import settings
from django.contrib.sites.models import Site
from web.nodes.locker import require_lock, model_lock
from web.nodes import ipcalc, data_archive
from web.nodes.common import load_plugin
from web.nodes.transitions import RouterTransition
from web.nodes.util import IPField, IPManager, queryset_by_ip
from web.generator.types import IfaceType
from web.dns.models import Zone, Record
from datetime import datetime, timedelta
import uuid

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
  ssid_backbone = models.CharField(max_length = 50)
  ssid_mobile = models.CharField(max_length = 50)
  captive_portal = models.BooleanField()
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

  def get_pools(self):
    """
    A helper method that returns the IP pools.
    """
    return queryset_by_ip(self.pools.all(), 'ip_subnet', 'description')

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
  Wireless = 2
  Test = 3
  Unknown = 4
  Mobile = 5
  Dead = 6

class Node(models.Model):
  """
  This class represents a single node in the network.
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
  node_type = models.IntegerField(default = NodeType.Wireless)
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
  
  # Peering history
  peer_history = models.ManyToManyField('self')

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
  loss_count = models.IntegerField(null = True)
  wifi_error_count = models.IntegerField(null = True)
  
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
    self.loss_count = None
    self.wifi_error_count = None

    # Mark related graph items for removal by the monitoring daemon
    self.graphitem_set.all().update(need_removal = True)
    GraphItem.objects.filter(type = GraphType.LQ, name = self.ip).update(need_removal = True)
    
    # Clear adjacency history
    self.peer_history.clear()
    
    # Clear renumbering notices
    self.awaiting_renumber = False
    self.renumber_notices.all().delete()
    
    # Clear tweets
    for t in self.tweets.all():
      t.delete()
  
  def adapt_to_router_type(self):
    """
    Ensures that new router type is compatible with current configuration.
    """
    from web.generator.models import Profile
    
    try:
      self.profile
    except Profile.DoesNotExist:
      return
    
    for entry in self.profile.template.adaptation_chain.all().order_by("priority"):
      cls = load_plugin(entry.class_name, required_super = RouterTransition)
      transition = cls()
      transition.adapt(self)
  
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
    return not self.system_node and self.geo_lat and self.geo_long and not self.is_dead()
  
  def get_graphs(self):
    """
    Returns a list of traffic graph items.
    """
    return self.graphitem_set.filter(parent = None).order_by('display_priority', 'name')

  def get_graph_timespans(self):
    """
    Returns a list of available graph image prefixes for different time
    periods for this node. At the moment only return a global list of
    prefixes.
    """
    return [prefix for  prefix, _ in settings.GRAPH_TIMESPANS]

  def is_down(self):
    """
    Returns true if the node is currently down.
    """
    return self.status not in (NodeStatus.Up, NodeStatus.Duped)

  def is_resettable(self):
    """
    Returns true if the node can be reset.
    """
    return self.status == NodeStatus.Down
  
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

  def is_wireless_node(self):
    """
    Returns true if the node is a wireless node.
    """
    return self.node_type in (NodeType.Wireless, NodeType.Test)

  def is_adjacency_important(self):
    """
    Returns true if the node's adjacency should be tracked.
    """
    return self.node_type in (NodeType.Wireless, NodeType.Server, NodeType.Unknown)

  def is_mobile_node(self):
    """
    Returns true if the node is a mobile node.
    """
    return self.node_type == NodeType.Mobile
  
  def is_dead(self):
    """
    Returns true if the node is marked as dead.
    """
    return self.node_type == NodeType.Dead
  
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
    return self.get_primary_subnet().count() > 0
  
  def get_primary_subnet(self):
    """
    Returns the primary node's subnet.
    """
    return self.subnet_set.ip_filter(ip_subnet__contains = "%s/32" % self.ip).filter(allocated = True).exclude(cidr = 0)
  
  def has_client_subnet(self, subnet=None):
    """
    Is node configured to have a subnet for clients?
    """
    if not subnet:
      subnets = self.subnet_set.filter(allocated = True, gen_iface_type = IfaceType.WiFi, cidr__lte = 28)
      if subnets:
        subnet = subnets[0]
    return subnet and subnet.cidr <= 28 and subnet.gen_iface_type == IfaceType.WiFi
  
  @property
  def configured_essid(self):
    """
    Returns the ESSID that this node should have configured.
    """
    essid = self.project.ssid
    if not self.has_client_subnet():
      # Node doesn't have a valid client subnet, so it is considered a
      # backbone node and this should be reflected in its ESSID
      essid = self.project.ssid_backbone
    
    if self.is_mobile_node():
      # Mobile nodes have their own ESSID assigned
      essid = self.project.ssid_mobile
    
    return essid
  
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
    if self.node_type == NodeType.Wireless:
      return _("Wireless node")
    elif self.node_type == NodeType.Server:
      return _("Server node")
    elif self.node_type == NodeType.Test:
      return _("Test node")
    elif self.node_type == NodeType.Mobile:
      return _("Mobile node")
    elif self.node_type == NodeType.Dead:
      return _("Dead node")
    else:
      return _("unknown node")

  def node_type_as_string_plural(self):
    """
    Returns node type as string.
    """
    if self.node_type == NodeType.Wireless:
      return _("Wireless nodes")
    elif self.node_type == NodeType.Server:
      return _("Server nodes")
    elif self.node_type == NodeType.Test:
      return _("Test nodes")
    elif self.node_type == NodeType.Mobile:
      return _("Mobile nodes")
    elif self.node_type == NodeType.Dead:
      return _("Dead nodes")
    else:
      return _("Unknown nodes")

  def get_warnings(self):
    """
    Returns a list of warnings for this node.
    """
    return self.warning_list.all().order_by('created_at')
  
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
  
  def has_allocated_subnets_to_lan(self):
    """
    Returns true if node has subnets allocated to the lan interface.
    """
    if self.subnet_set.filter(allocated = True, gen_iface_type = IfaceType.LAN):
      return True

    return False    
  
  def get_subnets(self):
    """
    Returns properly ordered subnets.
    """
    return queryset_by_ip(self.subnet_set.all(), "ip_subnet")
  
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
  
  def get_current_id(self):
    """
    Return current ID for the node. Node's name for registered node and node's pk for unknown nodes.
    """
    return self.pk if self.is_invalid() else self.name
  
  def get_full_url(self, use_https=getattr(settings, 'USE_HTTPS', None)):
    """
    Returns (full) absolute URL for the node.
    """
    base_url = "%s://%s" % ('https' if use_https else 'http', Site.objects.get_current().domain)
    return "%s%s" % (base_url, self.get_absolute_url())
  
  @models.permalink
  def get_absolute_url(self):
    """
    Returns (local) absolute URL for the node.
    """
    return ('view_node', (), {
      'node': self.get_current_id(),
    })
  
  def is_current_owner(self, request):
    """
    Returns true if current user owns this node.
    
    @param request: The request to get the current user from
    """
    return not self.is_invalid() and (self.owner == request.user or request.user.is_staff)
  
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
  vtime = models.FloatField()
  visible = models.BooleanField(db_index = True)
  # TODO need composite index on (src, dst)

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
  This class represents a subnet allocated to a specific node in the network.
  """
  node = models.ForeignKey(Node)
  subnet = models.CharField(max_length = 40)
  cidr = models.IntegerField()
  description = models.CharField(max_length = 200, null = True)
  allocated = models.BooleanField(default = False)
  allocated_at = models.DateTimeField(null = True)

  # Basic status (set by the monitor daemon)
  visible = models.BooleanField(db_index = True)
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
  
  def is_more_specific(self):
    """
    Returns true if this subnet is simply a more specific announce of one
    of node's allocated subnets.
    """
    return Subnet.objects.ip_filter(ip_subnet__contains = '%s/%s' % (self.subnet, self.cidr)).filter(node = self.node, allocated = True).count() > 0
  
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

    return queryset_by_ip(Subnet.objects.ip_filter(ip_subnet__conflicts = self.ip_subnet).exclude(cidr = 0).exclude(node = self.node), "ip_subnet")

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
  PacketLoss = 4
  WifiBitrate = 8
  WifiSignalNoise = 9
  WifiSNR = 6
  ETX = 11

  # Global graphs
  NodesByStatus = 1000
  
  # Graph ordering by type (top to bottom)
  ordering = [
    GatewayTraffic,
    Solar,
    Clients,
    Traffic,
    WifiSignalNoise,
    WifiBitrate,
    WifiCells,
    WifiSNR,
    OlsrPeers,
    PacketLoss,
    LQ,
    ETX,
    RTT,
    LoadAverage,
    MemUsage,
    NumProc
  ]

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
    elif type == GraphType.PacketLoss:
      return "packetloss"
    elif type == GraphType.WifiBitrate:
      return "wifibitrate"
    elif type == GraphType.WifiSignalNoise:
      return "wifisignalnoise"
    elif type == GraphType.WifiSNR:
      return "wifisnr"
    elif type == GraphType.ETX:
      return "etx"
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
  display_priority = 0

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
    return [prefix for prefix, _ in settings.GRAPH_TIMESPANS]

  def get_children(self):
    """
    Returns properly sorted graph item children.
    """
    if not self.children:
      return []

    return self.children.order_by('display_priority', 'name')

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
  title = models.CharField(max_length = 200)
  last_update = models.DateTimeField(null = True)
  dead = models.BooleanField(default = False, db_index = True)
  need_redraw = models.BooleanField(default = False, db_index = True)
  need_removal = models.BooleanField(default = False, db_index = True)
  display_priority = models.IntegerField(default = 0)
  
  def get_archive_data(self, start = None, sort = False):
    """
    Returns complete archive data for this graph. Will return an empty
    list when data archival is disabled in configuration.
    
    @param start: Start datetime
    @param sort: Set to true to sort by timestamp
    """
    return data_archive.fetch_data(self.pk, start = start, sort = sort)

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
    if prefix_len == 31:
      return None
    
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
      for child in queryset_by_ip(self.children.exclude(status = PoolStatus.Full), "ip_subnet"):
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
    
    if prefix_len == 31:
      return None
    
    pool = self.allocate_buddy(prefix_len)
    return pool

class StatsSolar(models.Model):
  """
  Solar dataset storage.
  """
  node = models.ForeignKey(Node)
  timestamp = models.DateTimeField()
  batvoltage = models.FloatField(null = True)
  solvoltage = models.FloatField(null = True)
  charge = models.FloatField(null = True)
  load = models.FloatField(null = True)
  state = models.IntegerField(null = True)

class EventSource:
  """
  Valid event source identifiers.
  """
  Monitor = 1
  UserReport = 2
  NodeDatabase = 3
  
  @staticmethod
  def to_string(source):
    """
    A helper method for transforming a source identifier to a
    human readable string.
    
    @param source: A valid source identifier
    """
    if source == EventSource.Monitor:
      return _("Monitor")
    elif source == EventSource.UserReport:
      return _("User report")
    elif source == EventSource.NodeDatabase:
      return _("Node database")
    else:
      return _("unknown")

  @staticmethod
  def to_identifier(source):
    """
    A helper method for transforming a source identifier to a
    machine readable string.
    
    @param source: A valid source identifier
    """
    if source == EventSource.Monitor:
      return "monitor"
    elif source == EventSource.UserReport:
      return "user"
    elif source == EventSource.NodeDatabase:
      return "database"
    else:
      return "unknown"

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
  AdjacencyEstablished = 19
  ConnectivityLoss = 20
  WifiErrors = 21

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
    elif code == EventCode.AdjacencyEstablished:
      return _("Adjacency established")
    elif code == EventCode.ConnectivityLoss:
      return _("Connectivity loss has been detected")
    elif code == EventCode.WifiErrors:
      return _("WiFi interface errors have been detected")
    else:
      return _("unknown event")

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
    return EventSource.to_string(self.source)

  def source_to_identifier(self):
    """
    Converts a source identifier to a string identifier (machine readable description).
    """
    return EventSource.to_identifier(self.source)

  def should_show_link(self):
    """
    Returns true if a link to event-generating node should be added
    to the notification message.
    """
    return self.code != EventCode.NodeRemoved

  @staticmethod
  def create_event(node, code, summary, source, data = "", aggregate = True):
    """
    Creates a new event.
    """
    # Check if this event should be supressed because it has already
    # occurred a short while ago
    events = Event.objects.filter(node = node, code = code, timestamp__gt = datetime.now() - timedelta(minutes = 30))
    if len(events) and code not in (EventCode.NodeRenamed,) and aggregate:
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
      'event' : event,
      'network' : { 'name'        : settings.NETWORK_NAME,
                    'home'        : settings.NETWORK_HOME,
                    'contact'     : settings.NETWORK_CONTACT,
                    'description' : getattr(settings, 'NETWORK_DESCRIPTION', None)
                  },
      'base_url' : "%s://%s" % ('https' if getattr(settings, 'USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
    })

    # Format node name and IP
    if event.node.name:
      name_ip = '%s/%s' % (event.node.ip, event.node.name)
    else:
      name_ip = event.node.ip

    # Should we really send an e-mail?
    if getattr(settings, 'EMAIL_TO_CONSOLE', None):
      print 'Subject: %s%s - %s' % (settings.EMAIL_SUBJECT_PREFIX or "", name_ip, event.code_to_string())
      print 'To: %s' % self.user.email
      print t.render(c)
    else:
      send_mail(
        '%s%s - %s' % (settings.EMAIL_SUBJECT_PREFIX or "", name_ip, event.code_to_string()),
        t.render(c),
        settings.EMAIL_EVENTS_SENDER,
        [self.user.email],
        fail_silently = True
      )

class WarningCode:
  """
  Valid warning code identifiers.
  """
  UnregisteredNode = 1
  DupedReplies = 2
  UnregisteredAnnounce = 3
  OwnNotAnnounced = 4
  TimeOutOfSync = 5
  NoBorderPeering = 6
  CaptivePortalDown = 7
  DnsDown = 8
  AnnounceConflict = 9
  MismatchedUuid = 10
  LongRenumber = 11
  OptPackageNotFound = 12
  BSSIDMismatch = 13
  ESSIDMismatch = 14
  VPNMacMismatch = 15
  VPNLimitMismatch = 16
  ChannelMismatch = 17
  McastRateMismatch = 18
  
  Custom = 100
  NodewatcherInterpretFailed = 101
  
  @staticmethod
  def to_description_string(code):
    """
    A helper method for transforming a warning code to a human
    readable description string.

    @param code: A valid warning code
    """
    if code == WarningCode.UnregisteredNode:
      return _("Node is not registered in the node database!")
    elif code == WarningCode.DupedReplies:
      return _("Monitor has received duplicate ICMP ECHO packets!")
    elif code == WarningCode.UnregisteredAnnounce:
      return _("Node is announcing subnets that are not allocated to it!")
    elif code == WarningCode.OwnNotAnnounced:
      return _("Node is not announcing its own allocated subnets!")
    elif code == WarningCode.TimeOutOfSync:
      return _("Node's local clock is more than 30 minutes out of sync!")
    elif code == WarningCode.NoBorderPeering:
      return _("Node requires direct border gateway peering (includes VPN servers) but has none!")
    elif code == WarningCode.CaptivePortalDown:
      return _("Captive portal daemon is down!")
    elif code == WarningCode.DnsDown:
      return _("Node's DNS resolver does not respond!")
    elif code == WarningCode.AnnounceConflict:
      return _("Node is announcing or has allocated one or more subnets that are in conflict with other nodes!")
    elif code == WarningCode.MismatchedUuid:
      return _("Reported node UUID does not match this node!")
    elif code == WarningCode.LongRenumber:
      return _("Node has been stuck in renumbering state for more than a week!")
    elif code == WarningCode.OptPackageNotFound:
      return _("Selected optional packages not found in installed node packages!")
    elif code == WarningCode.BSSIDMismatch:
      return _("WiFi BSSID does not match node configuration!")
    elif code == WarningCode.ESSIDMismatch:
      return _("WiFi ESSID does not match node configuration!")
    elif code == WarningCode.VPNMacMismatch:
      return _("Reported VPN MAC address does not match assigned MAC address!") 
    elif code == WarningCode.VPNLimitMismatch:
      return _("Reported VPN upload traffic limit does not match node configuration!")
    elif code == WarningCode.ChannelMismatch:
      return _("WiFi channel does not match node configuration!")
    elif code == WarningCode.McastRateMismatch:
      return _("WiFi multicast rate does not match node configuration!")
    elif code == WarningCode.NodewatcherInterpretFailed:
      return _("There was a problem while interpreting nodewatcher output from this node!")
    else:
      return _("unknown warning")
     
  @staticmethod
  def to_help_string(code):
    """
    A helper method for transforming a warning code to a human
    readable help string.

    @param code: A valid warning code
    """
    if code == WarningCode.UnregisteredNode:
      return _("Please register a node and use assigned configuration and IP address or contact network administrators to resolve the issue.")
    elif code == WarningCode.DupedReplies:
      return _("Probably just a temporary glitch but if it persists it could signify dangerous routing cycles.")
    elif code == WarningCode.UnregisteredAnnounce:
      return _("Please use only registered subnets otherwise serious conflicts between node configurations can happen.")
    elif code == WarningCode.OwnNotAnnounced:
      return _("Could be a temporary glitch but if it persists the node is probably not configured correctly or have not yet been flashed with new configuration.")
    elif code == WarningCode.TimeOutOfSync:
      return _("Clock can be out of sync just after the node boots up but if it persists it could signify a firmware bug.")
    elif code == WarningCode.NoBorderPeering:
      return _("Link to a VPN server has probably failed. If link does not reconnect soon please investigate node's Internet uplink.")
    elif code == WarningCode.CaptivePortalDown:
      return _("Could be a temporary glitch but if it persists it could signify a firmware bug.")
    elif code == WarningCode.DnsDown:
      return _("Could be a temporary glitch especially on nodes with unstable link to the network. If it persists it could signify a firmware bug or a network's DNS server problems.")
    elif code == WarningCode.AnnounceConflict:
      return _("Please check subnets list and investigate why the problem is occurring. Conflicts hinder connectivity in the network and are a really serious problem.")
    elif code == WarningCode.MismatchedUuid:
      return _("This is a bug or really strange things are happening. Please report it.")
    elif code == WarningCode.LongRenumber:
      return _("Please flash the node with new firmeware image to apply new configuration.")
    elif code == WarningCode.OptPackageNotFound:
      return _("If you do not want this package/s anymore please deselect it/them in node configuration.")
    elif code == WarningCode.BSSIDMismatch:
      return _("The node will not connect with other nodes in the network because of this. It is probably a bug. Please report it.")
    elif code == WarningCode.ESSIDMismatch:
      return _("If this is not intentional, it is a bug. Please report it. If it is intentional, please get in contact with network administrators to arrange a new project entry with your own ESSID for you.")
    elif code == WarningCode.VPNMacMismatch:
      return _("Download traffic limits will not work because of this. It is very likely a bug. Please report it.") 
    elif code == WarningCode.VPNLimitMismatch:
      return _("If you changed configured traffic limits you have to flash the node with new firmware image to apply new configuration. Or it could be a bug somewhere.")
    elif code == WarningCode.ChannelMismatch:
      return _("The node will not connect with other nodes in the network because of this. It is probably a bug. Please report it.")
    elif code == WarningCode.McastRateMismatch:
      return _("If this is not intentional, it is a bug. Please report it. If it is intentional, please get in contact with network administrators to arrange a configuration option in the firmware for it.")
    elif code == WarningCode.NodewatcherInterpretFailed:
      return _("Please check monitor log for more information or inform network administrator to do so. There is a bug somewhere.")
    else:
      return None

class NodeWarning(models.Model):
  """
  This model represents a warning that is issued to a node.
  """
  node = models.ForeignKey(Node, related_name = 'warning_list')
  code = models.IntegerField()
  source = models.IntegerField()
  details = models.TextField()
  created_at = models.DateTimeField()
  last_update = models.DateTimeField()
  dirty = models.BooleanField(default = False)
  
  def to_description_string(self):
    """
    Converts a warning to a human readable description string.
    """
    if self.code == WarningCode.Custom:
      return self.details
    else:
      return WarningCode.to_description_string(self.code)
    
  def to_help_string(self):
    """
    Converts a warning to a human readable help string.
    """
    if self.code == WarningCode.Custom:
      return None
    else:
      return WarningCode.to_help_string(self.code)
  
  def get_details(self):
    """
    Returns warning details.
    """
    if self.code == WarningCode.Custom:
      return None
    else:
      return self.details

  def source_to_string(self):
    """
    Converts a source identifier to a string.
    """
    return EventSource.to_string(self.source)
  
  def source_to_identifier(self):
    """
    Converts a source identifier to a string identifier (machine readable description).
    """
    return EventSource.to_identifier(self.source)

  @staticmethod
  def create(node, code, source, details = ''):
    """
    A helper method for creating new warnings or updating existing
    ones.
    
    @param nodes: A valid node to warn
    @param code: Warning code
    @param source: Warning source
    @param details: Warning details
    """
    node.warnings = True
    
    if code != WarningCode.Custom:
      warnings = NodeWarning.objects.filter(node = node, code = code)
      if warnings:
        for w in warnings:
          w.last_update = datetime.now()
          w.dirty = True
          w.source = source
          w.details = details
          w.save()
        
        return
      else:
        # Create a new warning since the old one does not exist
        pass
    else:
      # Custom warnings must always be created and never updated
      pass
    
    # New warning creation
    w = NodeWarning(node = node, code = code, source = source, details = details)
    w.last_update = w.created_at = datetime.now()
    w.dirty = True
    w.save()
    return w
  
  @staticmethod
  def clear_obsolete_warnings(source):
    """
    Clears all warnings that don't have the dirty flag.
    
    @param source: The source to delete for
    """
    NodeWarning.objects.filter(source = source, dirty = False).delete()

class InstalledPackage(models.Model):
  """
  This model represents an installed package reported via nodewatcher.
  """
  node = models.ForeignKey(Node)
  name = models.CharField(max_length = 100)
  version = models.CharField(max_length = 50)
  last_update = models.DateTimeField()

class Tweet(models.Model):
  """
  This class represents a tweet.
  """
  tweet_id = models.CharField(max_length = 50, null = False, unique = True)
  node = models.ForeignKey(Node, null = False, related_name = 'tweets')
  
  @staticmethod
  def tweets_enabled():
    """
    Returns true if tweets are enabled.
    """
    return getattr(settings, 'BITLY_LOGIN', None) and getattr(settings, 'BITLY_API_KEY', None) and getattr(settings, 'TWITTER_USERNAME', None) and getattr(settings, 'TWITTER_PASSWORD', None)
  
  @staticmethod
  def post_tweet(node, msg):
    """
    Posts a new tweet and links it with the specified node.
    
    @param node: Node instance
    @param msg: Message to tweet
    """
    if not Tweet.tweets_enabled():
      return
  
    import twitter
    twitter_api = twitter.Api(username = settings.TWITTER_USERNAME, password = settings.TWITTER_PASSWORD)
    status = twitter_api.PostUpdate(msg)
    
    t = Tweet(node = node, tweet_id = status.id)
    t.save()
    return t
  
  def delete(self, *args, **kwargs):
    """
    Deletes this tweet (also via the Twitter API).
    """
    if Tweet.tweets_enabled():
      try:
        import twitter
        twitter_api = twitter.Api(username = settings.TWITTER_USERNAME, password = settings.TWITTER_PASSWORD)
        twitter_api.DestroyStatus(self.tweet_id)
      except:
        pass
    
    super(Tweet, self).delete(*args, **kwargs)

class NodeNames(models.Model):
  """
  This model represents stored names for all nodes so that they can be retrieved also after renames.
  """
  name = models.CharField(max_length = 50, primary_key = True)
  node = models.ForeignKey(Node, related_name = 'names')

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
