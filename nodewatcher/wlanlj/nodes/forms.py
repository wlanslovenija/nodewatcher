from django import forms
from django.forms import widgets
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from wlanlj.nodes.models import Project, Pool, NodeStatus, Node, Subnet, SubnetStatus, AntennaType, PolarizationType, WhitelistItem, EventCode, EventSubscription, NodeType, Event, EventSource, SubscriptionType, Link, RenumberNotice, PoolStatus
from wlanlj.nodes import ipcalc
from wlanlj.nodes.sticker import generate_sticker
from wlanlj.generator.models import Template, Profile, OptionalPackage, gen_mac_address
from wlanlj.generator.types import IfaceType
from wlanlj.account.util import generate_random_password
from wlanlj.dns.models import Record
from wlanlj.policy.models import TrafficControlClass, Policy, PolicyFamily, PolicyAction
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
MAC_ADDR_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
MAC_ADDR_RE_ALT = re.compile(r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$') # Windows displays MAC address as physical address with dashes
NODE_NAME_RE = re.compile('(?:[a-zA-Z0-9]+-?[a-zA-Z0-9]*)*[a-zA-Z0-9]$')

class RegisterNodeForm(forms.Form):
  """
  A simple form for new node registration.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"))
  ip = forms.CharField(max_length = 40, required = False, label = _("IP address"))
  location = forms.CharField(required = False, max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea)
  url = forms.CharField(max_length = 200, required = False, label = _("Home page URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

  # Additional flags
  assign_ip = forms.BooleanField(required = False, label = _("No IP yet? Assign me one!"), initial = True)
  assign_subnet = forms.BooleanField(required = False, initial = True,
    label = _("Assign a new subnet")
  )
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = getattr((Project.objects.all() or [1])[0], "id", None),
    empty_label = None,
    label = _("Project")
  )
  node_type = forms.ChoiceField(
    choices = [
      (NodeType.Mesh, _("Mesh node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node")),
      (NodeType.Mobile, _("Mobile node"))
    ],
    initial = NodeType.Mesh,
    label = _("Node type")
  )
  
  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False)
  border_router = forms.BooleanField(required = False)

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all().order_by('name'),
    label = _("Router type"),
    required = False
  )
  channel = forms.ChoiceField(
    choices = [(0, _("Default"))] + [(x, x) for x in xrange(1, 11)],
    initial = 0,
    label = _("Channel"),
    required = False
  )
  root_pass = forms.CharField(required = False)
  use_vpn = forms.BooleanField(required = False, initial = True,
    label = _("Enable VPN"),
  )
  use_captive_portal = forms.BooleanField(required = False, initial = True,
    label = _("Enable captive portal")
  )
  lan_bridge = forms.BooleanField(required = False, initial = False,
    label = _("Enable LAN/WiFi bridge")
  )
  optional_packages = forms.ModelMultipleChoiceField(
    queryset = OptionalPackage.objects.all().order_by("fancy_name"),
    label = _("Optional packages"),
    required = False,
    widget = widgets.CheckboxSelectMultiple
  )
  
  # Traffic policy settings
  tc_ingress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Download limit"),
    required = False,
    empty_label = _("Unlimited")
  )
  tc_egress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Upload limit"),
    required = False,
    empty_label = _("Unlimited")
  )

  # Antenna type
  ant_external = forms.BooleanField(required = False, label = _("External antenna"))
  ant_polarization = forms.ChoiceField(
    choices = [
      (PolarizationType.Unknown, _("Unknown")),
      (PolarizationType.Horizontal, _("Horizontal")),
      (PolarizationType.Vertical, _("Vertical")),
      (PolarizationType.Circular, _("Circular"))
    ],
    required = False,
    label = _("Polarization")
  )
  ant_type = forms.ChoiceField(
    choices = [
      (AntennaType.Unknown, _("Unknown")),
      (AntennaType.Omni, _("Omni")),
      (AntennaType.Sector, _("Sector")),
      (AntennaType.Directional, _("Directional"))
    ],
    required = False,
    label = _("Type")
  )
  ant_conn = forms.ChoiceField(
    choices = [
      (4, _("Default")),
      (3, _("Automatic")),
      (0, _("First")),
      (1, _("Second"))
    ],
    initial = 4,
    label = _("Antenna connector"),
    required = False
  )

  # WAN options
  wan_dhcp = forms.BooleanField(required = False, label = _("WAN auto-configuration (DHCP)"), initial = True)
  wan_ip = forms.CharField(max_length = 45, required = False, label = _("WAN IP/mask"))
  wan_gw = forms.CharField(max_length = 40, required = False, label = _("WAN GW"))

  # Other options
  redundancy_req = forms.BooleanField(required = False, label = _("Enable no direct peering with a border gateway warning"))

  def clean(self):
    """
    Additional validation handler.
    """
    name = self.cleaned_data.get('name')
    ip = self.cleaned_data.get('ip')
    wan_dhcp = self.cleaned_data.get('wan_dhcp')
    wan_ip = self.cleaned_data.get('wan_ip')
    wan_gw = self.cleaned_data.get('wan_gw')
    geo_lat = self.cleaned_data.get('geo_lat')
    geo_long = self.cleaned_data.get('geo_long')
    location = self.cleaned_data.get('location')
    node_type = int(self.cleaned_data.get('node_type'))

    if not name:
      return

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may only contain letters, numbers and hyphens!"))

    if (geo_lat or geo_long) and (not (45 <= geo_lat <= 47) or not (13 <= geo_long <= 17)):
      raise forms.ValidationError(_("The specified latitude/longitude are out of range!"))
    
    if not location and node_type == NodeType.Mesh:
      raise forms.ValidationError(_("Location is required for mesh nodes!"))

    try:
      node = Node.objects.get(name = name)
      raise forms.ValidationError(_("The specified node name already exists!"))
    except Node.DoesNotExist:
      pass

    if ip and (not IPV4_ADDR_RE.match(ip) or ip.startswith('127.')):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))
    
    if self.cleaned_data.get('template'):
      if not wan_dhcp and (not wan_ip or not wan_gw):
        raise forms.ValidationError(_("IP and gateway are required for static WAN configuration!"))

      if wan_ip:
        try:
          network, cidr = wan_ip.split('/')
          cidr = int(cidr)
          if not IPV4_ADDR_RE.match(network) or network.startswith('127.'):
            raise ValueError
        except ValueError:
          raise forms.ValidationError(_("Enter subnet in CIDR notation!"))

        if not IPV4_ADDR_RE.match(wan_gw) or wan_gw.startswith('127.'):
          raise forms.ValidationError(_("Enter a valid gateway IP address!"))

        self.cleaned_data['wan_ip'] = network
        self.cleaned_data['wan_cidr'] = cidr

        net = ipcalc.Network(str(ipcalc.Network(network, cidr).network()), cidr)
        if ipcalc.IP(wan_gw) not in net:
          raise forms.ValidationError(_("Gateway must be part of specified WAN subnet!"))

    return self.cleaned_data
  
  def save(self, user):
    """
    Completes node registration.
    """
    ip = self.cleaned_data.get('ip')
    assign_subnet = self.cleaned_data.get('assign_subnet')
    project = self.cleaned_data.get('project')
    pool = project.pool
    subnet = None

    if not ip:
      # Assign a new IP address from the selected pool (if no IP address selected)
      node = Node()
      fresh_subnet = pool.allocate_subnet()
      net = ipcalc.Network(fresh_subnet.network, fresh_subnet.cidr)
      node.ip = str(net.host_first())
      
      # Create a new subnet for this node or use an existing one if available
      subnet = Subnet(node = node, subnet = fresh_subnet.network, cidr = fresh_subnet.cidr)
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
    else:
      # An IP has been entered, check if this node already exists
      try:
        node = Node.objects.get(ip = ip)
      except Node.DoesNotExist:
        node = Node(ip = ip)
      
      # Allocate a new subnet if requested and node has no subnets
      if assign_subnet and not node.subnet_set:
        fresh_subnet = pool.allocate_subnet()
        net = ipcalc.Network(fresh_subnet.network, fresh_subnet.cidr)
        subnet = Subnet(node = node, subnet = fresh_subnet.network, cidr = fresh_subnet.cidr)
        subnet.allocated = True
        subnet.allocated_at = datetime.now()
        subnet.status = SubnetStatus.NotAnnounced

    # Update node metadata
    node.name = self.cleaned_data.get('name').lower()
    node.project = project
    node.owner = user
    node.location = self.cleaned_data.get('location')
    node.geo_lat = self.cleaned_data.get('geo_lat')
    node.geo_long = self.cleaned_data.get('geo_long')
    node.ant_external = self.cleaned_data.get('ant_external')
    node.ant_polarization = self.cleaned_data.get('ant_polarization')
    node.ant_type = self.cleaned_data.get('ant_type')
    node.node_type = self.cleaned_data.get('node_type')
    node.notes = self.cleaned_data.get('notes')
    node.url = self.cleaned_data.get('url')
    node.redundancy_req = self.cleaned_data.get('redundancy_req')
    node.warnings = False

    for i in xrange(10):
      try:
        mac = gen_mac_address()
        Node.objects.get(vpn_mac_conf = mac)
      except Node.DoesNotExist: 
        node.vpn_mac_conf = mac
        break
    else:
      raise Exception, "unable to generate unique MAC"

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.status = NodeStatus.New
    node.save()

    # Create node traffic control policy
    tc_ingress = self.cleaned_data.get('tc_ingress')
    if tc_ingress:
      Policy.set_policy(node, node.vpn_mac_conf, PolicyAction.Shape, tc_ingress, PolicyFamily.Ethernet)
    
    # Create node profile for image generator
    if self.cleaned_data.get('template'):
      profile = Profile(node = node, template = self.cleaned_data.get('template'))
      if self.cleaned_data.get('channel') in ('', "0", None):
        profile.channel = node.project.channel
      else:
        profile.channel = self.cleaned_data.get('channel')
      profile.root_pass = self.cleaned_data.get('root_pass') or generate_random_password(8)
      profile.use_vpn = self.cleaned_data.get('use_vpn')
      profile.use_captive_portal = self.cleaned_data.get('use_captive_portal')
      profile.antenna = self.cleaned_data.get('ant_conn') or 0
      profile.lan_bridge = self.cleaned_data.get('lan_bridge') or False
      profile.wan_dhcp = self.cleaned_data.get('wan_dhcp')
      profile.wan_ip = self.cleaned_data.get('wan_ip')
      profile.wan_cidr = self.cleaned_data.get('wan_cidr')
      profile.wan_gw = self.cleaned_data.get('wan_gw')

      if self.cleaned_data.get('tc_egress'):
        profile.vpn_egress_limit = self.cleaned_data.get('tc_egress').bandwidth

      profile.save()

      profile.optional_packages = self.cleaned_data.get('optional_packages')
      profile.save()

    if subnet:
      subnet.node = node
      subnet.save()

    # Update DNS entries
    Record.update_for_node(node)

    # Generate node added event
    Event.create_event(node, EventCode.NodeAdded, '', EventSource.NodeDatabase)

    return node

class UpdateNodeForm(forms.Form):
  """
  A simple form for updating node information.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"))
  ip = forms.CharField(max_length = 40, required = False, label = _("IP address"))
  location = forms.CharField(required = False, max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  owner = forms.ModelChoiceField(
    User.objects.filter(is_active = True),
    initial = getattr((User.objects.filter(is_active = True) or [1])[0], "id", None),
    empty_label = None,
    label = _("Maintainer")
  )
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = getattr((User.objects.all() or [1])[0], "id", None),
    empty_label = None,
    label = _("Project")
  )
  node_type = forms.ChoiceField(
    choices = [
      (NodeType.Mesh, _("Mesh node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node")),
      (NodeType.Mobile, _("Mobile node"))
    ],
    initial = NodeType.Mesh,
    label = _("Node type")
  )
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea)
  url = forms.CharField(max_length = 200, required = False, label = _("Home page URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False)
  border_router = forms.BooleanField(required = False)

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all().order_by('name'),
    label = _("Router type"),
    required = False
  )
  channel = forms.ChoiceField(
    choices = [(x, x) for x in xrange(1, 11)],
    label = _("Channel"),
    initial = 8,
    required = False
  )
  root_pass = forms.CharField(required = False)
  use_vpn = forms.BooleanField(required = False,
    label = _("Enable VPN"),
    initial = True
  )
  use_captive_portal = forms.BooleanField(required = False,
    label = _("Enable captive portal"),
    initial = True
  )
  lan_bridge = forms.BooleanField(required = False, initial = False,
    label = _("Enable LAN/WiFi bridge")
  )
  optional_packages = forms.ModelMultipleChoiceField(
    queryset = OptionalPackage.objects.all().order_by("fancy_name"),
    label = _("Optional packages"),
    required = False,
    widget = widgets.CheckboxSelectMultiple
  )

  # Traffic policy settings
  tc_ingress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Download limit"),
    required = False,
    empty_label = _("Unlimited")
  )
  tc_egress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Upload limit"),
    required = False,
    empty_label = _("Unlimited")
  )

  # Antenna type
  ant_external = forms.BooleanField(required = False, label = _("External antenna"))
  ant_polarization = forms.ChoiceField(
    choices = [
      (PolarizationType.Unknown, _("Unknown")),
      (PolarizationType.Horizontal, _("Horizontal")),
      (PolarizationType.Vertical, _("Vertical")),
      (PolarizationType.Circular, _("Circular"))
    ],
    required = False,
    label = _("Polarization")
  )
  ant_type = forms.ChoiceField(
    choices = [
      (AntennaType.Unknown, _("Unknown")),
      (AntennaType.Omni, _("Omni")),
      (AntennaType.Sector, _("Sector")),
      (AntennaType.Directional, _("Directional"))
    ],
    required = False,
    label = _("Type")
  )
  ant_conn = forms.ChoiceField(
    choices = [
      (4, _("Default")),
      (3, _("Automatic")),
      (0, _("First")),
      (1, _("Second"))
    ],
    initial = 4,
    label = _("Antenna connector"),
    required = False
  )

  # WAN options
  wan_dhcp = forms.BooleanField(required = False, label = _("WAN auto-configuration (DHCP)"), initial = True)
  wan_ip = forms.CharField(max_length = 45, required = False, label = _("WAN IP/mask"))
  wan_gw = forms.CharField(max_length = 40, required = False, label = _("WAN GW"))

  # Other options
  redundancy_req = forms.BooleanField(required = False, label = _("Enable no direct peering with a border gateway warning"))

  def __init__(self, node, *args, **kwargs):
    """
    Class constructor.
    """
    super(UpdateNodeForm, self).__init__(*args, **kwargs)
    self.__current_node = node

  def clean(self):
    """
    Additional validation handler.
    """
    name = self.cleaned_data.get('name')
    ip = self.cleaned_data.get('ip')
    wan_dhcp = self.cleaned_data.get('wan_dhcp')
    wan_ip = self.cleaned_data.get('wan_ip')
    wan_gw = self.cleaned_data.get('wan_gw')
    geo_lat = self.cleaned_data.get('geo_lat')
    geo_long = self.cleaned_data.get('geo_long')
    use_vpn = self.cleaned_data.get('use_vpn')
    node = self.__current_node
    template = self.cleaned_data.get('template')
    location = self.cleaned_data.get('location')
    node_type = int(self.cleaned_data.get('node_type'))

    if not name:
      return

    try:
      if use_vpn and template and not template.iface_lan and node.has_allocated_subnets(IfaceType.LAN):
        raise forms.ValidationError(_("The specified router only has one ethernet port! You have already added some LAN subnets to it, so you cannot enable VPN!"))
    except Profile.DoesNotExist:
      pass

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may only contain letters, numbers and hyphens!"))

    if (geo_lat or geo_long) and (not (45 <= geo_lat <= 47) or not (13 <= geo_long <= 17)):
      raise forms.ValidationError(_("The specified latitude/longitude are out of range!"))

    if not location and node_type == NodeType.Mesh:
      raise forms.ValidationError(_("Location is required for mesh nodes!"))

    try:
      node = Node.objects.get(name = name)
      if node != self.__current_node:
        raise forms.ValidationError(_("The specified node name already exists!"))
    except Node.DoesNotExist:
      pass

    if ip and (not IPV4_ADDR_RE.match(ip) or ip.startswith('127.')):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))
    
    if self.cleaned_data.get('template'):
      if not wan_dhcp and (not wan_ip or not wan_gw):
        raise forms.ValidationError(_("IP and gateway are required for static WAN configuration!"))

      if wan_ip:
        try:
          network, cidr = wan_ip.split('/')
          cidr = int(cidr)
          if not IPV4_ADDR_RE.match(network) or network.startswith('127.'):
            raise ValueError
        except ValueError:
          raise forms.ValidationError(_("Enter subnet in CIDR notation!"))

        if not IPV4_ADDR_RE.match(wan_gw) or wan_gw.startswith('127.'):
          raise forms.ValidationError(_("Enter a valid gateway IP address!"))

        self.cleaned_data['wan_ip'] = network
        self.cleaned_data['wan_cidr'] = cidr

        net = ipcalc.Network(str(ipcalc.Network(network, cidr).network()), cidr)
        if ipcalc.IP(wan_gw) not in net:
          raise forms.ValidationError(_("Gateway must be part of specified WAN subnet!"))

    return self.cleaned_data
  
  def save(self, node, user):
    """
    Completes node data update.
    """
    ip = self.cleaned_data.get('ip')
    oldName = node.name
    oldProject = node.project
    
    # Update node metadata
    node.name = self.cleaned_data.get('name').lower()
    node.owner = self.cleaned_data.get('owner')
    node.location = self.cleaned_data.get('location')
    node.geo_lat = self.cleaned_data.get('geo_lat')
    node.geo_long = self.cleaned_data.get('geo_long')
    node.ant_external = self.cleaned_data.get('ant_external')
    node.ant_polarization = self.cleaned_data.get('ant_polarization')
    node.ant_type = self.cleaned_data.get('ant_type')
    node.project = self.cleaned_data.get('project')
    node.node_type = self.cleaned_data.get('node_type')
    node.notes = self.cleaned_data.get('notes')
    node.url = self.cleaned_data.get('url')
    node.redundancy_req = self.cleaned_data.get('redundancy_req')

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.save()

    # Update node traffic control policy
    tc_ingress = self.cleaned_data.get('tc_ingress')
    if tc_ingress:
      Policy.set_policy(node, node.vpn_mac_conf, PolicyAction.Shape, tc_ingress, PolicyFamily.Ethernet)
    else:
      try:
        node.gw_policy.get(addr = node.vpn_mac_conf, family = PolicyFamily.Ethernet).delete()
      except Policy.DoesNotExist:
        pass

    # Update DNS records on name changes
    if oldName != node.name or oldProject != node.project:
      Record.update_for_node(node, old_name = oldName, old_project = oldProject)

      # Generate node renamed event
      Event.create_event(node, EventCode.NodeRenamed, '', EventSource.NodeDatabase, data = 'Old name: %s\n  New name: %s' % (oldName, node.name))

    # Update node profile for image generator
    try:
      profile = node.profile
    except Profile.DoesNotExist:
      profile = None

    if self.cleaned_data.get('template'):
      if not profile:
        profile = Profile(node = node, template = self.cleaned_data.get('template'))

      if not self.cleaned_data.get('channel'):
        profile.channel = node.project.channel
      else:
        profile.channel = self.cleaned_data.get('channel')
      profile.template = self.cleaned_data.get('template')
      profile.root_pass = self.cleaned_data.get('root_pass')
      profile.use_vpn = self.cleaned_data.get('use_vpn')
      profile.use_captive_portal = self.cleaned_data.get('use_captive_portal')
      profile.antenna = self.cleaned_data.get('ant_conn') or 0
      profile.lan_bridge = self.cleaned_data.get('lan_bridge') or False
      profile.wan_dhcp = self.cleaned_data.get('wan_dhcp')
      profile.wan_ip = self.cleaned_data.get('wan_ip')
      profile.wan_cidr = self.cleaned_data.get('wan_cidr')
      profile.wan_gw = self.cleaned_data.get('wan_gw')

      if self.cleaned_data.get('tc_egress'):
        profile.vpn_egress_limit = self.cleaned_data.get('tc_egress').bandwidth
      else:
        profile.vpn_egress_limit = None
 
      profile.save()

      profile.optional_packages = self.cleaned_data.get('optional_packages')
      profile.save()
    elif profile:
      profile.delete()

class AllocateSubnetForm(forms.Form):
  """
  A simple form for subnet allocation.
  """
  network = forms.CharField(max_length = 50, required = False)
  description = forms.CharField(max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  iface_type = forms.ChoiceField(
    choices = [
      (IfaceType.WiFi, 'WiFi'),
      (IfaceType.LAN, 'LAN')
    ],
    initial = IfaceType.LAN,
    label = _("Interface")
  )
  prefix_len = forms.ChoiceField(
    choices = [
      (24, '/24'),
      (25, '/25'),
      (26, '/26'),
      (27, '/27'),
      (28, '/28')
    ],
    initial = 27,
    label = _("Prefix length")
  )
  dhcp = forms.BooleanField(required = False, initial = True, label = _("DHCP announce"))
  
  def __init__(self, node, *args, **kwargs):
    """
    Class constructor.
    """
    super(AllocateSubnetForm, self).__init__(*args, **kwargs)
    self.__node = node

  def clean(self):
    """
    Additional validation handler.
    """
    type = int(self.cleaned_data.get('iface_type'))
    if type == IfaceType.WiFi:
      try:
        subnet = Subnet.objects.get(node = self.__node, gen_iface_type = IfaceType.WiFi)
        raise forms.ValidationError(_("Only one WiFi subnet may be allocated to a node!"))
      except Subnet.DoesNotExist:
        pass
    
    try:
      if type == IfaceType.LAN and not self.__node.profile.template.iface_lan and self.__node.profile.use_vpn:
        raise forms.ValidationError(_("The specified router only has one ethernet port! You have already enabled VPN, so you cannot add subnets to LAN port!"))
    except Profile.DoesNotExist:
      pass

    if self.cleaned_data.get('network'):
      try:
        network, cidr = self.cleaned_data.get('network').split('/')
        cidr = int(cidr)
        if not IPV4_ADDR_RE.match(network) or network.startswith('127.'):
          raise ValueError
      except ValueError:
        raise forms.ValidationError(_("Enter subnet in CIDR notation!"))

      # Check if the given subnet already exists
      if Subnet.is_allocated(network, cidr):
        raise forms.ValidationError(_("Specified subnet is already in use!"))

      # Check if the given subnet is part of any allocation pools (unless it is allocatable)
      if Pool.contains_network(network, cidr):
        project = self.__node.project
        
        if project.pool and project.pool.reserve_subnet(network, cidr, check_only = True):
          self.cleaned_data['reserve'] = True
        else:
          raise forms.ValidationError(_("Specified subnet is part of an allocation pool and cannot be manually allocated!"))

      self.cleaned_data['network'] = network
      self.cleaned_data['cidr'] = cidr

    return self.cleaned_data

  def save(self, node):
    """
    Completes subnet allocation.
    """
    network = self.cleaned_data.get('network')
    cidr = self.cleaned_data.get('cidr')
    
    if network:
      if self.cleaned_data['reserve']:
        # We should reserve this manually allocated subnet in the project pool
        if not node.project.pool.reserve_subnet(network, cidr):
          return
      
      subnet = Subnet(node = node)
      subnet.subnet = network
      subnet.cidr = cidr
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
      subnet.description = self.cleaned_data.get('description')
      subnet.gen_iface_type = self.cleaned_data.get('iface_type')
      subnet.gen_dhcp = self.cleaned_data.get('dhcp')
      subnet.save()
    else:
      pool = node.project.pool
      allocation = pool.allocate_subnet(int(self.cleaned_data.get('prefix_len')) or 27)
      subnet = Subnet(node = node, subnet = allocation.network, cidr = allocation.cidr)
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
      subnet.description = self.cleaned_data.get('description')
      subnet.gen_iface_type = self.cleaned_data.get('iface_type')
      subnet.gen_dhcp = self.cleaned_data.get('dhcp')
      subnet.save()

    # Remove any already announced subnets that are the same subnet
    Subnet.objects.filter(node = node, subnet = subnet.subnet, cidr = subnet.cidr, allocated = False).delete()

class EditSubnetForm(forms.Form):
  """
  A simple form for editing a subnet.
  """
  description = forms.CharField(max_length = 200)

class WhitelistMacForm(forms.Form):
  """
  A simple form for whitelisting a MAC address.
  """
  mac = forms.CharField(max_length = 17, label = _("MAC address"))
  description = forms.CharField(max_length = 200, label = _("Description"), widget = widgets.TextInput(attrs = {'size': '40'}))
  
  def clean(self):
    """
    Additional validation handler.
    """
    mac = self.cleaned_data.get('mac')
    if MAC_ADDR_RE_ALT.match(mac):
      self.cleaned_data['mac'] = mac.replace('-', ':')
    elif not MAC_ADDR_RE.match(mac):
      raise forms.ValidationError(_("Enter a valid MAC address!"))

    try:
      item = WhitelistItem.objects.get(mac = mac)
      raise forms.ValidationError(_("Specified MAC address is already whitelisted!"))
    except WhitelistItem.DoesNotExist:
      pass

    return self.cleaned_data

  def save(self, user):
    """
    Saves whitelist entry.
    """
    item = WhitelistItem(owner = user)
    item.mac = self.cleaned_data.get('mac').upper()
    item.description = self.cleaned_data.get('description')
    item.registred_at = datetime.now()
    item.save()

class InfoStickerForm(forms.Form):
  """
  A simple form for whitelisting a MAC address.
  """
  name = forms.CharField(max_length = 50, label = _("Your name"))
  phone = forms.CharField(max_length = 50, label = _("Phone number"))
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = getattr((User.objects.all() or [1])[0], "id", None),
    label = _("Project")
  )
  
  def save(self, user):
    """
    Saves info sticker data and generates the sticker.
    """
    name = self.cleaned_data.get('name')
    phone = self.cleaned_data.get('phone')
    project = self.cleaned_data.get('project')

    if name == user.name and phone == user.phone and project == user.project:
      regenerate = False
    else:
      user.name = name
      user.phone = phone
      user.project = project
      regenerate = True

    return generate_sticker(user, regenerate)

class EventSubscribeForm(forms.Form):
  """
  A simple form for subscribing to an event.
  """
  type = forms.ChoiceField(
    choices = [
      (SubscriptionType.SingleNode, _("Match a single node")),
      (SubscriptionType.AllNodes, _("Match all nodes")),
      (SubscriptionType.MyNodes, _("Match only own nodes"))
    ],
    label = _("Type")
  )
  node = forms.ModelChoiceField(
    Node.objects.exclude(status = NodeStatus.Invalid),
    label = _("Node"),
    required = False,
    empty_label = None
  )
  code = forms.ChoiceField(
    choices = [
      (0, _('Any event')),
      (EventCode.NodeDown, _('Node has gone down')),
      (EventCode.NodeUp, _('Node has come up')),
      (EventCode.UptimeReset, _('Node has been rebooted')),
      (EventCode.PacketDuplication, _('Packet duplication detected')),
      (EventCode.IPShortage, _('IP shortage on WiFi subnet')),
      (EventCode.ChannelChanged, _('WiFi channel has changed')),
      (EventCode.RedundancyLoss, _('Redundant link to border gateway has gone down')),
      (EventCode.RedundancyRestored, _("Redundant link to border gateway has been restored")),
      (EventCode.VersionChange, _("Firmware version has changed")),
      (EventCode.CaptivePortalDown, _("Captive portal has failed")),
      (EventCode.CaptivePortalUp, _("Captive portal has been restored")),
      (EventCode.SubnetHijacked, _("Node is causing a subnet collision")),
      (EventCode.SubnetRestored, _("Subnet collision is no longer present")),
      (EventCode.DnsResolverFailed, _("DNS resolver has failed")),
      (EventCode.DnsResolverRestored, _("DNS resolver restored")),
      (EventCode.NodeAdded, _("A new node has been registered")),
      (EventCode.NodeRenamed, _("Node has been renamed")),
      (EventCode.NodeRemoved, _("Node has been removed")),
      (EventCode.NodeRenumbered, _("Node has been renumbered")),
    ],
    required = False
  )

  def save(self, user):
    """
    Saves whitelist entry.
    """
    s = EventSubscription(user = user)
    s.type = int(self.cleaned_data.get('type'))
    
    if s.type == SubscriptionType.SingleNode:
      s.node = self.cleaned_data.get('node') or None
    else:
      s.node = None

    s.code = int(self.cleaned_data.get('code')) or None
    s.save()

class RenumberAction:
  """
  Valid renumber actions.
  """
  Keep = 0
  Remove = -1
  Renumber = -2
  SetManually = -3

class RenumberForm(forms.Form):
  """
  A form for renumbering a node.
  """
  manual_ip = forms.CharField(max_length = 40, required = False)
  
  def __init__(self, user, node, *args, **kwargs):
    """
    Class constructor.
    """
    super(RenumberForm, self).__init__(*args, **kwargs)
    self.__node = node
    
    # Use renumber with subnet only when this is possible
    self.fields['primary_ip'] = forms.ChoiceField(
      choices = [
        (RenumberAction.SetManually, _("Set manually"))
      ],
      initial = RenumberAction.SetManually
    )
    
    if node.is_primary_ip_in_subnet():
      self.fields['primary_ip'].choices.insert(0,
        (RenumberAction.Renumber, _("Renumber with subnet"))
      )
      self.fields['primary_ip'].initial = RenumberAction.Renumber
    else:
      self.fields['primary_ip'].choices.insert(0,
        (RenumberAction.Keep, _("Keep")),
      )
      self.fields['primary_ip'].initial = RenumberAction.Keep
    
    if not user.is_staff:
      del self.fields['primary_ip'].choices[1]
    
    # Setup dynamic form fields, depending on how may subnets a node has
    primary = node.subnet_set.ip_filter(ip_subnet__contains = "%s/32" % node.ip).filter(allocated = True).exclude(cidr = 0)
    
    for subnet in node.subnet_set.filter(allocated = True).order_by('ip_subnet'):
      pools = []
      for pool in Pool.objects.filter(parent = None).exclude(status = PoolStatus.Full).order_by('network'):
        pools.append((pool.pk, _("Renumber to %s/%s [%s]") % (pool.network, pool.cidr, pool.description)))
      
      choices = [
        (RenumberAction.Keep, _("Keep")),
        (RenumberAction.Remove, _("Remove"))
      ]
      
      # Primary subnets should not be removed
      if primary and primary[0] == subnet:
        del choices[1]
      
      self.fields['subnet_%s' % subnet.pk] = forms.ChoiceField(
        choices = choices + pools,
        initial = RenumberAction.Keep
      )
  
  def get_subnet_fields(self):
    """
    A helper method that returns all subnet fields in order.
    """
    for subnet in self.__node.subnet_set.filter(allocated = True).order_by('ip_subnet'):
      field = self['subnet_%s' % subnet.pk]
      field.model = subnet
      yield field
  
  def clean(self):
    """
    Additional validation handler.
    """
    # Check that the manually set primary IP is not in conflict with anything
    action = int(self.cleaned_data.get('primary_ip'))
    manual_ip = self.cleaned_data.get('manual_ip')
    
    if action == RenumberAction.SetManually:
      # Validate entered IP address
      if not manual_ip or not IPV4_ADDR_RE.match(manual_ip) or manual_ip.startswith('127.'):
        raise forms.ValidationError(_("Enter a valid primary IP address!"))
      
      # Check if the given address already exists
      if Subnet.is_allocated(manual_ip, 32):
        raise forms.ValidationError(_("Specified primary IP address is already in use!"))

      # Check if the given subnet is part of any allocation pools
      if Pool.contains_network(manual_ip, 32):
        raise forms.ValidationError(_("Specified primary IP is part of an allocation pool and cannot be manually allocated!"))
    
    return self.cleaned_data
  
  def save(self):
    """
    Performs the actual renumbering.
    """
    # We must ensure exclusive access during node updates as otherwise this might happen
    # in the middle of a monitor update and this would cause unwanted consequences
    self.__node.ensure_exclusive_access()
    
    # Determine what subnet primary IP belonged to
    primary = self.__node.subnet_set.ip_filter(ip_subnet__contains = "%s/32" % self.__node.ip).filter(allocated = True).exclude(cidr = 0)
    renumber_primary = False
    old_router_id = self.__node.ip
    
    # Renumber subnets first
    for subnet in self.__node.subnet_set.filter(allocated = True).order_by('ip_subnet')[:]:
      action = int(self.cleaned_data.get('subnet_%s' % subnet.pk))
      
      if action == RenumberAction.Keep:
        pass
      elif action == RenumberAction.Remove:
        subnet.delete()
      else:
        # This means we should renumber to some other pool
        pool = Pool.objects.get(pk = action)
        new_subnet = pool.allocate_subnet(prefix_len = subnet.cidr)
        
        # If the old subnet has been the source of node's primary IP remember that
        save_primary = (not renumber_primary and primary and primary[0] == subnet)
        
        # Remove old subnet and create a new one; it is deleted here so the old allocation
        # is returned to the pool and all status info is reset
        subnet.delete()
        
        s = Subnet(node = self.__node, subnet = new_subnet.network, cidr = new_subnet.cidr)
        s.allocated = True
        s.allocated_at = datetime.now()
        s.status = SubnetStatus.NotAnnounced
        s.save()
        
        if save_primary:
          primary = s
          renumber_primary = True
    
    # The subnet have now been renumbered, check if we need to renumber the primary IP
    action = int(self.cleaned_data.get('primary_ip'))
    router_id_changed = False
    if action == RenumberAction.Keep:
      pass
    elif action == RenumberAction.SetManually:
      self.__node.ip = self.cleaned_data.get('manual_ip')
      router_id_changed = True
    elif action == RenumberAction.Renumber and renumber_primary:
      net = ipcalc.Network(primary.subnet, primary.cidr)
      self.__node.ip = str(net.host_first())
      router_id_changed = True
    
    # Remove conflicting invalid nodes (another node with the IP we just renumbered to)
    Node.objects.filter(ip = self.__node.ip, status = NodeStatus.Invalid).delete()
    
    # Node has been renumbered, reset monitoring status as this node is obviously not
    # visible right after renumbering.
    if router_id_changed:
      # Update node's DNS record
      Record.update_for_node(self.__node)
      
      if not self.__node.is_pending():
        self.__node.status = NodeStatus.Down
        self.__node.peers = 0
        Link.objects.filter(src = self.__node).delete()
        Link.objects.filter(dst = self.__node).delete()
        self.__node.subnet_set.filter(allocated = False).delete()
        self.__node.subnet_set.all().update(status = SubnetStatus.NotAnnounced)
        
        # Setup a node renumbered notice (if one doesn't exist yet)
        try:
          notice = RenumberNotice.objects.get(node = self.__node)
        except RenumberNotice.DoesNotExist:
          notice = RenumberNotice(node = self.__node)
          notice.original_ip = old_router_id
          notice.renumbered_at = datetime.now()
          notice.save()
        
        self.__node.awaiting_renumber = True
    
    self.__node.save()
    
    # Generate node renumbered event
    Event.create_event(self.__node, EventCode.NodeRenumbered, '', EventSource.NodeDatabase,
                       data = 'Old address: %s' % old_router_id)

