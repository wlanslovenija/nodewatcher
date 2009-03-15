from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.template import loader, Context
from wlanlj.nodes.locker import require_lock
from wlanlj.nodes import ipcalc
from wlanlj.generator.types import IfaceType
from wlanlj.dns.models import Zone, Record
from datetime import datetime, timedelta

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
  
  # Magic marker
  UserSpecifiedMark = 100

  # Additional status codes that can only be set explicitly
  # by the node's owner or an administrator.
  UnknownProblems = 100
  Building = 101
  NeedEquipment = 102
  NeedHelp = 103
  TakenDown = 104

class NodeType:
  """
  Valid node types.
  """
  Server = 1
  Mesh = 2
  Test = 3
  Unknown = 4

class Node(models.Model):
  """
  This class represents a single node in the mesh.
  """
  ip = models.CharField(max_length = 40, primary_key = True)
  name = models.CharField(max_length = 50, null = True, unique = True)
  owner = models.ForeignKey(User, null = True)
  location = models.CharField(max_length = 200, null = True)
  project = models.ForeignKey(Project, null = True)

  # System nodes are special purpuse nodes that provide external
  # services such as VPN
  system_node = models.BooleanField(default = False)
  border_router = models.BooleanField(default = False)
  node_type = models.IntegerField(default = NodeType.Mesh)

  # Geographical location
  geo_lat = models.FloatField(null = True)
  geo_long = models.FloatField(null = True)

  # Antenna information
  ant_external = models.BooleanField(default = False)
  ant_polarization = models.IntegerField(default = PolarizationType.Unknown)
  ant_type = models.IntegerField(default = AntennaType.Unknown)

  # Basic status (set by the monitor daemon)
  warnings = models.BooleanField(default = False)
  status = models.IntegerField(null = True)
  peers = models.IntegerField(null = True, default = 0)
  peer_list = models.ManyToManyField('self', through = 'Link', symmetrical = False)
  last_seen = models.DateTimeField(null = True)
  channel = models.IntegerField(null = True)

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
    return self.graphitem_set.all().order_by('-type', 'name')

  def is_down(self):
    """
    Returns true if the node is currently down.
    """
    return self.status not in (NodeStatus.Up, NodeStatus.Duped)

  def is_invalid(self):
    """
    Returns true if the node is invalid.
    """
    return self.status == NodeStatus.Invalid

  def is_mesh_node(self):
    """
    Returns true if the node is a mesh node.
    """
    return self.node_type in (NodeType.Mesh, NodeType.Test)

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
    else:
      return _("Unknown")

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
    else:
      return _("Unknown nodes")

  def get_warnings(self):
    """
    Returns a list of warnings for this node.
    """
    w = []
    if self.status == NodeStatus.Invalid:
      w.append(_("Node is not registred in the node database!"))

    if self.status == NodeStatus.Duped:
      w.append(_("Monitor has received duplicate ICMP ECHO packets!"))

    if self.subnet_set.filter(status = SubnetStatus.NotAllocated):
      w.append(_("Node is announcing subnets, that are not allocated to it!"))

    if self.subnet_set.filter(status = SubnetStatus.NotAnnounced):
      w.append(_("Node is not announcing its own allocated subnets!"))

    if self.has_time_sync_problems():
      w.append(_("Node's local clock is more than 30 minutes out of sync!"))

    return w

  def has_allocated_subnets(self, type = IfaceType.WiFi):
    """
    Returns true if node has subnets allocated to the specified interface.
    """
    if self.subnet_set.filter(allocated = True, gen_iface_type = type):
      return True

    return False

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
      return _("Unknown")

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
      return _("Unknown")

  def status_as_string(self):
    """
    Returns this node's status as a human readable string.
    """
    if self.status == NodeStatus.Up:
      return "up"
    elif self.status == NodeStatus.Visible:
      return "visible"
    elif self.status == NodeStatus.Down:
      return "down"
    elif self.status == NodeStatus.Duped:
      return "duped"
    elif self.status == NodeStatus.Invalid:
      return "invalid"
    elif self.status == NodeStatus.UnknownProblems:
      return "problems"
    elif self.status == NodeStatus.Building:
      return "building"
    elif self.status == NodeStatus.NeedEquipment:
      return "needequip"
    elif self.status == NodeStatus.NeedHelp:
      return "needhelp"
    elif self.status == NodeStatus.TakenDown:
      return "takendown"
    elif self.status == NodeStatus.New:
      return "new"
    else:
      return "unknown"

  def __unicode__(self):
    """
    Returns a string representation of this node.
    """
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

class Subnet(models.Model):
  """
  This class represents a subnet allocated to a specific node in the
  wifi mesh.
  """
  node = models.ForeignKey(Node)
  subnet = models.CharField(max_length = 200)
  cidr = models.IntegerField()
  description = models.CharField(max_length = 200, null = True)
  allocated = models.BooleanField(default = False)
  allocated_at = models.DateTimeField(null = True)

  # Basic status (set by the monitor daemon)
  status = models.IntegerField()
  last_seen = models.DateTimeField(null = True)

  # Generator attributes
  gen_iface_type = models.IntegerField(default = IfaceType.WiFi)
  gen_dhcp = models.BooleanField(default = True)
  
  def is_wifi(self):
    """
    Returns true if this subnet is a wireless one.
    """
    return self.gen_iface_type == IfaceType.WiFi

  @staticmethod
  def is_allocated(network, cidr):
    """
    Returns true if a node has the specified subnet allocated. This is
    currently an expensive operation.
    """
    net = ipcalc.Network(network, cidr)
    for x in Subnet.objects.filter(allocated = True):
      comp_net = ipcalc.Network(x.subnet, x.cidr)
      if net in comp_net or comp_net in net:
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
    else:
      return "unknown"
  
  def __unicode__(self):
    """
    Returns a string representation of this subnet.
    """
    return u"%s/%d" % (self.subnet, self.cidr)

class APClient(models.Model):
  """
  This class represents an end-user client connected to one of the AP nodes
  being tracked via the captive portal.
  """
  node = models.ForeignKey(Node)
  ip = models.CharField(max_length = 40)
  last_update = models.DateTimeField(null = True)

  # Transfer statistics (set by the monitor daemon)
  uploaded = models.IntegerField()
  downloaded = models.IntegerField()

class GraphType:
  """
  A list of valid graph types.
  """
  Traffic = 10
  Clients = 20
  RTT = 2
  LQ = 3
  Solar = 30

class GraphItem(models.Model):
  """
  This class represents a graph of some node's parameter.
  """
  node = models.ForeignKey(Node)
  type = models.IntegerField()
  name = models.CharField(max_length = 50)
  rra = models.CharField(max_length = 200)
  graph = models.CharField(max_length = 200)
  title = models.CharField(max_length = 50)
  last_update = models.DateTimeField(null = True)

class WhitelistItem(models.Model):
  """
  This class represents a whitelisted MAC address.
  """
  owner = models.ForeignKey(User)
  mac = models.CharField(max_length = 50)
  registred_at = models.DateTimeField()

class PoolAllocationError(Exception):
  pass

class PoolFamily:
  """
  Possible address families.
  """
  Ipv4 = 4
  Ipv6 = 6

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
  allocated = models.BooleanField(default = False)
  default_prefix_len = models.IntegerField(default = 27)
  last_alloc_network = models.CharField(max_length = 50, null = True)
  last_alloc_cidr = models.IntegerField(null = True)

  @staticmethod
  def contains_network(network, cidr):
    """
    Returns true if any pools contain this network.
    """
    net = ipcalc.Network(network, cidr)
    for x in Pool.objects.filter(parent = None):
      comp_net = ipcalc.Network(x.network, x.cidr)
      if net in comp_net or comp_net in net:
        return True

    return False

  def __unicode__(self):
    """
    Returns a string representation of this pool.
    """
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

    if self.family != PoolFamily.Ipv4:
      raise PoolAllocationError('Only IPv4 allocations are currently supported!')

    if self.parent:
      raise PoolAllocationError('Attempted to allocate from child pool!')

    # First check if there are any children that are marked as free
    for c in self.children.filter(allocated = False, cidr = prefix_len):
      c.allocated = True
      c.save()
      return c

    # No children have been found, create new kids
    parent_net = ipcalc.Network(self.network, self.cidr)
    if not self.last_alloc_network:
      net = ipcalc.Network(self.network, prefix_len)
      if net not in parent_net:
        raise PoolAllocationError('Given prefix exceeds pool size!')

      allocation = (self.network, prefix_len)
    else:
      net = ipcalc.Network(self.last_alloc_network, self.last_alloc_cidr)
      net = ipcalc.Network(long(net) + net.size(), prefix_len)
      if net not in parent_net:
        raise PoolAllocationError('Given prefix exceeds pool size!')

      allocation = (str(net.network()), prefix_len)
    
    # Check if this is actually still free
    if Subnet.is_allocated(*allocation):
      raise PoolAllocationError('Subnet allocation conflict found! All automatic allocations have been suspended. Contact network operations immediately!')

    # Create a new child
    child = Pool(parent = self, family = self.family)
    child.network, child.cidr = allocation
    child.allocated = True
    child.default_prefix_len = 0
    self.last_alloc_network, self.last_alloc_cidr = allocation
    child.save()
    self.save()
    return child

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

  NodeAdded = 100

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
    elif code == EventCode.NodeAdded:
      return _("A new node has been registred")
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
      return _("Unknown source")
  
  @staticmethod
  def create_event(node, code, summary, source, data = ""):
    """
    Creates a new event.
    """
    # Check if this event should be supressed because it has already
    # occurred a short while ago
    events = Event.objects.filter(node = node, code = code, timestamp__gt = datetime.now() - timedelta(minutes = 30))
    if len(events):
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
      models.Q(node = self.node) | models.Q(node__isnull = True),
      models.Q(code = self.code) | models.Q(code__isnull = True)
    )

    for subscription in subscriptions:
      subscription.notify(self)

class EventSubscription(models.Model):
  """
  Event subscription model.
  """
  user = models.ForeignKey(User)
  node = models.ForeignKey(Node, null = True)
  active = models.BooleanField(default = True)
  code = models.IntegerField(null = True)

  def code_to_string(self):
    """
    Converts an event code to a human readable string.
    """
    return EventCode.to_string(self.code)

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

    send_mail(
      '[wlan-lj] ' + event.node.ip + '/' +  _("Event notification") + ' - ' + event.code_to_string(),
      t.render(c),
      'events@wlan-lj.net',
      [self.user.email],
      fail_silently = False
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
  try:
    subnet = Pool.objects.get(network = instance.subnet, cidr = instance.cidr)
    subnet.allocated = False
    subnet.save()
  except Pool.DoesNotExist:
    pass

def node_on_delete_callback(sender, **kwargs):
  """
  On delete callback for Nodes.
  """
  Record.remove_for_node(kwargs['instance'])

models.signals.pre_delete.connect(subnet_on_delete_callback, sender = Subnet)
models.signals.pre_delete.connect(node_on_delete_callback, sender = Node)

