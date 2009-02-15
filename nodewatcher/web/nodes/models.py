from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from ljwifi.nodes.locker import require_lock
from ljwifi.nodes import ipcalc
from ljwifi.generator.types import IfaceType

class Project(models.Model):
  """
  This class represents a project. Each project can contains some
  nodes and is also assigned a default IP allocation pool.
  """
  name = models.CharField(max_length = 50)
  description = models.CharField(max_length = 200)
  pool = models.ForeignKey('Pool')

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

class Node(models.Model):
  """
  This class represents a single node in the mesh.
  """
  ip = models.CharField(max_length = 40, primary_key = True)
  name = models.CharField(max_length = 50, null = True)
  owner = models.ForeignKey(User, null = True)
  location = models.CharField(max_length = 200, null = True)
  project = models.ForeignKey(Project, null = True)

  # System nodes are special purpuse nodes that provide external
  # services such as VPN
  system_node = models.BooleanField(default = False)
  border_router = models.BooleanField(default = False)

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

    return w
  
  def has_allocated_subnets(self):
    """
    Returns true if node has subnets allocated to the WiFi interface.
    """
    if self.subnet_set.filter(allocated = True, gen_iface_type = IfaceType.WiFi):
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

class Link(models.Model):
  """
  This class represents a peering relationship between nodes.
  """
  src = models.ForeignKey(Node, related_name = 'src')
  dst = models.ForeignKey(Node, related_name = 'dst')
  lq = models.FloatField()
  ilq = models.FloatField()
  etx = models.FloatField()

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

  # Transfer statistics (set by the monitor daemon)
  uploaded = models.IntegerField()
  downloaded = models.IntegerField()

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

models.signals.pre_delete.connect(subnet_on_delete_callback, sender = Subnet)

