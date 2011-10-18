from django import forms
from django.forms import widgets
from django.db import transaction, models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core import validators as core_validators
from django.conf import settings
from web.nodes.models import Project, Pool, NodeStatus, Node, Subnet, SubnetStatus, AntennaType, PolarizationType, WhitelistItem, EventCode, EventSubscription, NodeType, Event, EventSource, SubscriptionType, Link, RenumberNotice, PoolStatus, GraphType, NodeNames
from web.nodes import ipcalc
from web.nodes.sticker import generate_sticker
from web.nodes.transitions import validates_node_configuration
from web.nodes.common import FormWithWarnings
from web.nodes.utils import queryset_by_ip
from web.generator.models import Template, Profile, OptionalPackage, gen_mac_address
from web.generator.types import IfaceType
from web.account.utils import generate_random_password
from web.dns.models import Record
from web.policy.models import TrafficControlClass, Policy, PolicyFamily, PolicyAction
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'^\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b$')
MAC_ADDR_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
MAC_ADDR_RE_ALT = re.compile(r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$') # Windows displays MAC address as physical address with dashes
# This format is used also in node.js so keep it in sync
NODE_NAME_RE = re.compile(r'^[a-z](?:-?[a-z0-9]+)*$')

class RegisterNodeForm(forms.Form):
  """
  A simple form for new node registration.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"), widget = widgets.TextInput(attrs = {'size': '40'}))
  ip = forms.CharField(max_length = 40, required = False, label = _("IP address"))
  location = forms.CharField(required = False, max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  geo_lat = forms.FloatField(required = False, label = _("Latitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea(attrs={'cols':'80', 'rows': 5}))
  url = forms.URLField(max_length = 200, required = False, label = _("Home page URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

  # Additional flags
  assign_ip = forms.BooleanField(required = False, label = _("Assign automatically from the IP pool"), initial = True)
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = getattr((Project.objects.all() or [1])[0], "id", None),
    empty_label = None,
    label = _("Project")
  )
  pool = forms.ModelChoiceField(
    # Cannot use queryset_by_ip as proper queryset is expected
    Pool.objects.exclude(status = PoolStatus.Full).filter(parent = None).order_by('description', 'ip_subnet'),
    empty_label = None,
    label = _("IP pool")
  )
  prefix_len = forms.TypedChoiceField(
    choices = [(x, "/{0}".format(x)) for x in xrange(21, 33)],
    initial = 27,
    coerce = int,
    label = _("Subnet size")
  )
  node_type = forms.ChoiceField(
    choices = [
      (NodeType.Wireless, _("Wireless node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node")),
      (NodeType.Mobile, _("Mobile node"))
    ],
    initial = NodeType.Wireless,
    label = _("Node type")
  )
  
  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False, label = _("System node"))
  border_router = forms.BooleanField(required = False, label = _("Border router"))
  vpn_server = forms.BooleanField(required = False, label = _("VPN server"))

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all().order_by('name'),
    label = _("Router type"),
    required = False
  )
  channel = forms.ChoiceField(
    choices = [(0, _("Default"))] + [(x, x) for x in xrange(1, 15)],
    initial = 0,
    label = _("Channel"),
    required = False
  )
  root_pass = forms.CharField(required = False,
    validators = [core_validators.MinLengthValidator(4)],
    initial = generate_random_password(8),
    label = _("Root password"),
  )
  use_vpn = forms.BooleanField(required = False, initial = True,
    label = _("Enable VPN"),
  )
  lan_bridge = forms.BooleanField(required = False, initial = False,
    label = _("Enable LAN/WiFi bridge"),
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
    empty_label = _("Unlimited"),
  )
  tc_egress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Upload limit"),
    required = False,
    empty_label = _("Unlimited"),
  )

  # Antenna type
  ant_external = forms.BooleanField(required = False, label = _("External antenna"))
  ant_polarization = forms.ChoiceField(
    choices = [
      (PolarizationType.Unknown, _("unknown")),
      (PolarizationType.Horizontal, _("Horizontal")),
      (PolarizationType.Vertical, _("Vertical")),
      (PolarizationType.Dual, _("Horizontal and Vertical")),
      (PolarizationType.Circular, _("Circular"))
    ],
    required = False,
    label = _("Polarization")
  )
  ant_type = forms.ChoiceField(
    choices = [
      (AntennaType.Unknown, _("unknown")),
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
  wan_ip = forms.CharField(max_length = 45, required = False, label = _("WAN IP address/mask"))
  wan_gw = forms.CharField(max_length = 40, required = False, label = _("WAN gateway IP address"))

  # Other options
  redundancy_req = forms.BooleanField(required = False, label = _("Require direct connection to a VPN server"))

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
    project = self.cleaned_data.get('project')
    pool = self.cleaned_data.get('pool')
    prefix_len = self.cleaned_data.get('prefix_len')
    root_pass = self.cleaned_data.get('root_pass')
    
    if prefix_len == 0:
      prefix_len = None
    
    if not name:
      return

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may contain only lower case letters, numbers and hyphens!"))

    if not location and node_type == NodeType.Wireless:
      raise forms.ValidationError(_("Location is required for wireless nodes!"))
    
    if (not geo_lat or not geo_long) and node_type == NodeType.Wireless:
      raise forms.ValidationError(_("Geographical coordinates are required for wireless nodes!"))

    try:
      node = Node.objects.get(name = name)
      raise forms.ValidationError(_("The specified node name already exists!"))
    except Node.DoesNotExist:
      pass

    if ip and (not IPV4_ADDR_RE.match(ip) or ip.startswith('127.')):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))
    
    if not project.pools.filter(pk = pool.pk).count():
      raise forms.ValidationError(_("The specified IP allocation pool cannot be used with selected project!"))
    
    if prefix_len and not (pool.min_prefix_len <= prefix_len <= pool.max_prefix_len):
      raise forms.ValidationError(_("The specified prefix length cannot be allocated from selected pool!"))
    
    if ip:
      # Compute proper subnet IP otherwise checks will fail because of a misaligned address
      net = ipcalc.Network(ip, prefix_len)
      sub_ip = str(net.network())
      
      if not pool.reserve_subnet(sub_ip, prefix_len or 32, check_only = True):
        raise forms.ValidationError(_("The node IP (%(subnet)s/%(cidr)s) you have manually entered cannot be allocated from the selected pool (%(pool)s)! This might be because the subnet is already in use by another node or is not a part of the selected pool.") % { 'subnet' : ip, 'cidr' : prefix_len or 32, 'pool' : str(pool) })
    
    if self.cleaned_data.get('template'):
      if not root_pass:
        raise forms.ValidationError(_("Root password is required!"))
      
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
  
  @validates_node_configuration
  def save(self, user):
    """
    Completes node registration.
    """
    ip = self.cleaned_data.get('ip')
    project = self.cleaned_data.get('project')
    pool = self.cleaned_data.get('pool')
    prefix_len = self.cleaned_data.get('prefix_len')
    if prefix_len == 0:
      prefix_len = None
    subnet = None

    if not ip:
      # Assign a new IP address from the selected pool (if no IP address selected)
      node = Node()
      fresh_subnet = pool.allocate_subnet(prefix_len)
      net = ipcalc.Network(fresh_subnet.network, fresh_subnet.cidr)
      node.ip = str(net.host_first())
      
      # Create a new subnet for this node or use an existing one if available
      subnet = Subnet(node = node, subnet = fresh_subnet.network, cidr = fresh_subnet.cidr)
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
    else:
      # When prefix is not available we should use /32
      if prefix_len is None:
        prefix_len = 32
      
      net = ipcalc.Network(ip, prefix_len)
      sub_ip = str(net.network())
      
      # Check if this node already exists
      try:
        node = Node.objects.get(ip = str(net.host_first()))
      except Node.DoesNotExist:
        node = Node(ip = str(net.host_first()))
      
      # Reserve existing IP in the pool
      pool.reserve_subnet(sub_ip, prefix_len)
      try:
        subnet = Subnet.objects.get(node = node, subnet = sub_ip, cidr = prefix_len)
        subnet.status = SubnetStatus.AnnouncedOk
      except Subnet.DoesNotExist:
        subnet = Subnet(node = node, subnet = sub_ip, cidr = prefix_len)
        subnet.status = SubnetStatus.NotAnnounced
      
      subnet.allocated = True
      subnet.allocated_at = datetime.now()

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
      node.vpn_server = self.cleaned_data.get('vpn_server')
    
    if user.is_staff or getattr(settings, 'NONSTAFF_BORDER_ROUTERS', False):
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
      profile.root_pass = self.cleaned_data.get('root_pass')
      profile.use_vpn = self.cleaned_data.get('use_vpn')
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
    
    # Registers node name
    NodeNames(name = node.name, node = node).save()

    # Generate node added event
    Event.create_event(node, EventCode.NodeAdded, '', EventSource.NodeDatabase,
                       data = 'Maintainer: %s' % node.owner.username)

    self.node = node
    return node

class UpdateNodeForm(forms.Form):
  """
  A simple form for updating node information.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"), widget = widgets.TextInput(attrs = {'size': '40'}))
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
      (NodeType.Wireless, _("Wireless node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node")),
      (NodeType.Mobile, _("Mobile node")),
      (NodeType.Dead, _("Dead node"))
    ],
    initial = NodeType.Wireless,
    label = _("Node type")
  )
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea(attrs={'cols':'80', 'rows': 5}))
  url = forms.URLField(max_length = 200, required = False, label = _("Home page URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False, label = _("System node"))
  border_router = forms.BooleanField(required = False, label = _("Border router"))
  vpn_server = forms.BooleanField(required = False, label = _("VPN server"))

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all().order_by('name'),
    label = _("Router type"),
    required = False,
  )
  channel = forms.ChoiceField(
    choices = [(x, x) for x in xrange(1, 15)],
    label = _("Channel"),
    initial = 8,
    required = False,
  )
  root_pass = forms.CharField(required = False,
    validators = [core_validators.MinLengthValidator(4)],
    initial = generate_random_password(8),
    label = _("Root password"),
  )
  use_vpn = forms.BooleanField(required = False,
    label = _("Enable VPN"),
    initial = True,
  )
  lan_bridge = forms.BooleanField(required = False, initial = False,
    label = _("Enable LAN/WiFi bridge"),
  )
  optional_packages = forms.ModelMultipleChoiceField(
    queryset = OptionalPackage.objects.all().order_by("fancy_name"),
    label = _("Optional packages"),
    required = False,
    widget = widgets.CheckboxSelectMultiple,
  )

  # Traffic policy settings
  tc_ingress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Download limit"),
    required = False,
    empty_label = _("Unlimited"),
  )
  tc_egress = forms.ModelChoiceField(
    TrafficControlClass.objects.all().order_by("bandwidth"),
    label = _("Upload limit"),
    required = False,
    empty_label = _("Unlimited"),
  )

  # Antenna type
  ant_external = forms.BooleanField(required = False, label = _("External antenna"))
  ant_polarization = forms.ChoiceField(
    choices = [
      (PolarizationType.Unknown, _("Unknown")),
      (PolarizationType.Horizontal, _("Horizontal")),
      (PolarizationType.Vertical, _("Vertical")),
      (PolarizationType.Dual, _("Horizontal and Vertical")),
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
  wan_ip = forms.CharField(max_length = 45, required = False, label = _("WAN IP address/mask"))
  wan_gw = forms.CharField(max_length = 40, required = False, label = _("WAN gateway IP address"))

  # Other options
  redundancy_req = forms.BooleanField(required = False, label = _("Require direct connection to a VPN server"))

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
    project = self.cleaned_data.get('project')
    root_pass = self.cleaned_data.get('root_pass')

    if not name:
      return

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may only contain letters, numbers and hyphens!"))

    if not location and node_type == NodeType.Wireless:
      raise forms.ValidationError(_("Location is required for wireless nodes!"))
    
    if (not geo_lat or not geo_long) and node_type == NodeType.Wireless:
      raise forms.ValidationError(_("Geographical coordinates are required for wireless nodes!"))

    try:
      node = Node.objects.get(name = name)
      if node != self.__current_node:
        raise forms.ValidationError(_("The specified node name already exists!"))
    except Node.DoesNotExist:
      pass
    
    if ip and (not IPV4_ADDR_RE.match(ip) or ip.startswith('127.')):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))
    
    if self.cleaned_data.get('template'):
      if not root_pass:
        raise forms.ValidationError(_("Root password is required!"))
      
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
  
  @validates_node_configuration
  def save(self, node, user):
    """
    Completes node data update.
    """
    self.requires_firmware_update = False
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
      node.vpn_server = self.cleaned_data.get('vpn_server')
    
    if user.is_staff or getattr(settings, 'NONSTAFF_BORDER_ROUTERS', False):
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
      if oldName != node.name:
        Event.create_event(node, EventCode.NodeRenamed, '', EventSource.NodeDatabase, data = 'Old name: %s\n  New name: %s' % (oldName, node.name))

    # Update node profile for image generator
    try:
      profile = node.profile
    except Profile.DoesNotExist:
      profile = None

    if self.cleaned_data.get('template'):
      if not profile:
        profile = Profile(node = node, template = self.cleaned_data.get('template'))
      
      # Handle potential hardware changes
      new_template = self.cleaned_data.get('template')
      if profile.template != new_template:
        # Rename traffic graphs to preserve history
        node.rename_graphs(GraphType.Traffic, profile.template.iface_wifi, new_template.iface_wifi)
      
      def set_and_check(**kwargs):
        for key, value in kwargs.iteritems():
          field = getattr(profile, key)
          meta = profile._meta.get_field(key)
          prep = meta.get_db_prep_value(value)
          
          if isinstance(meta, models.ManyToManyField):
            if set([m.pk for m in field.all()]) != set([m.pk for m in value]):
              self.requires_firmware_update = True
          elif field != prep:
            self.requires_firmware_update = True
          
          setattr(profile, key, value)
      
      if not self.cleaned_data.get('channel'):
        set_and_check(channel = node.project.channel)
      else:
        set_and_check(channel = self.cleaned_data.get('channel'))
      
      set_and_check(
        template = self.cleaned_data.get('template'),
        root_pass = self.cleaned_data.get('root_pass'),
        use_vpn = self.cleaned_data.get('use_vpn'),
        antenna = self.cleaned_data.get('ant_conn') or 0,
        lan_bridge = self.cleaned_data.get('lan_bridge') or False,
        wan_dhcp = self.cleaned_data.get('wan_dhcp'),
        wan_ip = self.cleaned_data.get('wan_ip'),
        wan_cidr = self.cleaned_data.get('wan_cidr'),
        wan_gw = self.cleaned_data.get('wan_gw')
      )
      
      if self.cleaned_data.get('tc_egress'):
        set_and_check(vpn_egress_limit = self.cleaned_data.get('tc_egress').bandwidth)
      else:
        set_and_check(vpn_egress_limit = None)
 
      profile.save()

      set_and_check(optional_packages = self.cleaned_data.get('optional_packages'))
      profile.save()
    elif profile and (settings.IMAGE_GENERATOR_ENABLED or settings.DEBUG):
      profile.delete()
    
    # Registers node name
    NodeNames(name = node.name, node = node).save()
    
    return node

class AllocateSubnetForm(forms.Form):
  """
  A simple form for subnet allocation.
  """
  network = forms.CharField(max_length = 50, required = False)
  description = forms.CharField(max_length = 200, initial = 'LAN', widget = widgets.TextInput(attrs = {'size': '40'}))
  prefix_len = forms.IntegerField(
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
    
    # Populate prefix length choices
    primary_pool = self.__node.get_primary_ip_pool() 
    self.fields['pool'] = forms.ModelChoiceField(
      # Cannot use queryset_by_ip as proper queryset is expected
      node.project.pools.exclude(status = PoolStatus.Full).filter(parent = None).order_by('description', 'ip_subnet'),
      empty_label = None,
      label = _("IP pool"),
      initial = primary_pool.pk if primary_pool else 0
    )
  
  def get_pools(self):
    """
    A helper method that returns the IP pools.
    """
    return queryset_by_ip(self.__node.project.pools.exclude(status = PoolStatus.Full).filter(parent = None), 'ip_subnet', 'description')
  
  def clean(self):
    """
    Additional validation handler.
    """
    pool = self.cleaned_data.get('pool')

    if self.cleaned_data.get('network'):
      try:
        network, cidr = self.cleaned_data.get('network').split('/')
        cidr = int(cidr)
        if not IPV4_ADDR_RE.match(network) or network.startswith('127.'):
          raise ValueError
      except ValueError:
        raise forms.ValidationError(_("Enter subnet in CIDR notation!"))

      # Check if the given subnet already exists
      if Subnet.is_allocated(network, cidr, exclude_node = self.__node):
        raise forms.ValidationError(_("Specified subnet is already in use!"))

      # Check if the given subnet is part of any allocation pools (unless it is allocatable)
      if Pool.contains_network(network, cidr):
        if pool.reserve_subnet(network, cidr, check_only = True):
          self.cleaned_data['reserve'] = True
        else:
          raise forms.ValidationError(_("Specified subnet is part of another allocation pool and cannot be manually allocated!"))

      self.cleaned_data['network'] = network
      self.cleaned_data['cidr'] = cidr

    return self.cleaned_data

  @validates_node_configuration
  def save(self, node):
    """
    Completes subnet allocation.
    """
    network = self.cleaned_data.get('network')
    cidr = self.cleaned_data.get('cidr')
    pool = self.cleaned_data.get('pool')
    
    if network:
      if self.cleaned_data['reserve']:
        # We should reserve this manually allocated subnet in the project pool
        if not pool.reserve_subnet(network, cidr):
          return
      
      subnet = Subnet(node = node)
      subnet.subnet = network
      subnet.cidr = cidr
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
      subnet.description = self.cleaned_data.get('description')
      subnet.gen_iface_type = IfaceType.LAN
      subnet.gen_dhcp = self.cleaned_data.get('dhcp')
      subnet.save()
    else:
      allocation = pool.allocate_subnet(int(self.cleaned_data.get('prefix_len')) or 27)
      subnet = Subnet(node = node, subnet = allocation.network, cidr = allocation.cidr)
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
      subnet.description = self.cleaned_data.get('description')
      subnet.gen_iface_type = IfaceType.LAN
      subnet.gen_dhcp = self.cleaned_data.get('dhcp')
      subnet.save()

    # Remove any already announced subnets that are the same subnet
    Subnet.objects.filter(node = node, subnet = subnet.subnet, cidr = subnet.cidr, allocated = False).delete()
    
    return node

class EditSubnetForm(forms.Form):
  """
  A simple form for editing a subnet.
  """
  description = forms.CharField(max_length = 200, required = False)
  dhcp = forms.BooleanField(required = False, initial = True, label = _("DHCP announce"))
  
  def __init__(self, node, *args, **kwargs):
    """
    Class constructor.
    """
    super(EditSubnetForm, self).__init__(*args, **kwargs)
    self.__node = node
  
  @validates_node_configuration
  def save(self, subnet):
    """
    Completes subnet edit.
    """
    subnet.description = self.cleaned_data.get('description')
    subnet.gen_dhcp = self.cleaned_data.get('dhcp')
    subnet.save()
    return self.__node

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
    if not self.cleaned_data.get('mac'):
      # This field is required
      return self.cleaned_data
    
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
      (SubscriptionType.MyNodes, _("Match only my nodes"))
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
      (EventCode.RedundancyLoss, _('Redundant link to VPN server has gone down')),
      (EventCode.RedundancyRestored, _("Redundant link to VPN server has been restored")),
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
      (EventCode.AdjacencyEstablished, _("Adjacency established")),
      (EventCode.ConnectivityLoss, _("Connectivity loss has been detected")),
      (EventCode.WifiErrors, _("WiFi interface errors have been detected"))
    ],
    required = False
  )
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request', None)
    super(EventSubscribeForm, self).__init__(*args, **kwargs)
    self.request = request

  def clean(self):
    """
    Additional validation handler to check if user has e-mail address configured.
    """
    if not self.request.user.email:
      raise forms.ValidationError(_("Specified user does not have an e-mail configured!"))
    
    try:
      filter_type = int(self.cleaned_data.get('type'))
      filter_node = self.cleaned_data.get('node') if filter_type == SubscriptionType.SingleNode else None
      filter_code = int(self.cleaned_data.get('code')) or None
      
      EventSubscription.objects.get(
        user = self.request.user,
        type = filter_type,
        node = filter_node,
        code = filter_code
      )
      
      # If we are here, a duplicate event subscription exists
      raise forms.ValidationError(_("Specified event subscription filter already exists!"))
    except EventSubscription.DoesNotExist:
      pass
    
    return self.cleaned_data

  def save(self, user):
    """
    Saves event subscription entry.
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

class RenumberForm(FormWithWarnings):
  """
  A form for renumbering a node.
  """
  
  def __init__(self, user, node, *args, **kwargs):
    """
    Class constructor.
    """
    super(RenumberForm, self).__init__(*args, **kwargs)
    self.__node = node
    
    # Setup dynamic form fields, depending on how may subnets a node has
    primary = node.subnet_set.ip_filter(ip_subnet__contains = "%s/32" % node.ip).filter(allocated = True).exclude(cidr = 0)
    
    for subnet in queryset_by_ip(node.subnet_set.filter(allocated = True), 'ip_subnet'):
      pools = []
      for pool in queryset_by_ip(node.project.pools.exclude(status = PoolStatus.Full), 'ip_subnet', 'description'):
        pools.append((pool.pk, _("Renumber to %s [%s/%s]") % (pool.description, pool.network, pool.cidr)))
      
      choices = [
        (RenumberAction.Keep, _("Keep")),
        (RenumberAction.Remove, _("Remove"))
      ]
      
      # Primary subnets should not be removed
      if primary and primary[0] == subnet:
        del choices[1]
      
      self.fields['subnet_%s' % subnet.pk] = forms.ChoiceField(
        choices = choices + pools,
        initial = RenumberAction.Keep,
        widget = forms.Select(attrs = { 'class' : 'subnet' })
      )
      
      # Field for choosing new subnet prefix size
      self.fields['prefix_%s' % subnet.pk] = forms.IntegerField(required = False, initial = 27)
      
      # Field for manual subnet specification
      self.fields['manual_%s' % subnet.pk] = forms.CharField(required = False)
  
  def get_pools(self):
    """
    A helper method that returns all allocations pools.
    """
    return queryset_by_ip(self.__node.project.pools.exclude(status = PoolStatus.Full), 'ip_subnet', 'description')
  
  def get_subnet_fields(self):
    """
    A helper method that returns all subnet fields in order.
    """
    for subnet in queryset_by_ip(self.__node.subnet_set.filter(allocated = True), 'ip_subnet'):
      field = self['subnet_%s' % subnet.pk]
      field.model = subnet
      field.prefix = 'prefix_%s' % subnet.pk
      field.manual_ip = self['manual_%s' % subnet.pk]
      yield field
  
  def clean(self):
    """
    Additional validation handler.
    """
    for subnet in queryset_by_ip(self.__node.subnet_set.filter(allocated = True), 'ip_subnet'):
      manual_ip = self.cleaned_data.get('manual_%s' % subnet.pk)
      if not manual_ip:
        continue
      
      action = int(self.cleaned_data.get('subnet_%s' % subnet.pk))
      prefix_len = int(self.cleaned_data.get('prefix_%s' % subnet.pk) or 27)
      
      # Validate IP address format
      if not IPV4_ADDR_RE.match(manual_ip):
        raise forms.ValidationError(_("Enter a valid IP address or leave the subnet field empty!"))
      
      # Validate pool status
      pool = Pool.objects.get(pk = action)
      if not pool.reserve_subnet(manual_ip, prefix_len, check_only = True):
        raise forms.ValidationError(_("Subnet %(subnet)s/%(prefix_len)d cannot be allocated from %(pool)s!") % { 'subnet' : manual_ip, 'prefix_len' : prefix_len, 'pool' : unicode(pool) })
    
    return self.cleaned_data
  
  def save(self):
    """
    Performs the actual renumbering.
    """
    # We must ensure exclusive access during node updates as otherwise this might happen
    # in the middle of a monitor update and this would cause unwanted consequences
    self.__node.ensure_exclusive_access()
    
    # Determine what subnet primary IP belonged to
    primary = self.__node.get_primary_subnet()
    renumber_primary = False
    old_router_id = self.__node.ip
    
    # Renumber subnets first
    for subnet in queryset_by_ip(self.__node.subnet_set.filter(allocated = True), 'ip_subnet')[:]:
      action = int(self.cleaned_data.get('subnet_%s' % subnet.pk))
      prefix_len = int(self.cleaned_data.get('prefix_%s' % subnet.pk) or 27)
      manual_ip = self.cleaned_data.get('manual_%s' % subnet.pk)
      
      if action == RenumberAction.Keep:
        pass
      elif action == RenumberAction.Remove:
        subnet.delete()
      else:
        # This means we should renumber to some other pool
        pool = Pool.objects.get(pk = action)
        if manual_ip:
          new_subnet = pool.reserve_subnet(manual_ip, prefix_len)
        else:
          new_subnet = pool.allocate_subnet(prefix_len)
        
        # If the old subnet has been the source of node's primary IP remember that
        save_primary = (not renumber_primary and primary and primary[0] == subnet)
        
        # Remove old subnet and create a new one; it is deleted here so the old allocation
        # is returned to the pool and all status info is reset
        subnet.delete()
        
        s = Subnet(node = self.__node, subnet = new_subnet.network, cidr = new_subnet.cidr)
        s.allocated = True
        s.allocated_at = datetime.now()
        s.status = SubnetStatus.NotAnnounced
        s.description = subnet.description
        s.gen_iface_type = subnet.gen_iface_type
        s.gen_dhcp = subnet.gen_dhcp
        s.save()
        
        if save_primary:
          primary = s
          renumber_primary = True
    
    # The subnet have now been renumbered, check if we need to renumber the primary IP
    router_id_changed = False
    if renumber_primary:
      net = ipcalc.Network(primary.subnet, primary.cidr)
      self.__node.ip = str(net.host_first())
      router_id_changed = True
    
    # Remove conflicting invalid nodes (another node with the IP we just renumbered to)
    existing_nodes = Node.objects.filter(ip = self.__node.ip, status = NodeStatus.Invalid)
    if existing_nodes.count() > 0:
      self.warning_or_continue(_("There is an existing but unregistered node with the same primary IP address you are currently renumbering to! If you continue with this operation, this invalid node will be replaced."))
    existing_nodes.delete()
    
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
          
          if notice.original_ip == self.__node.ip:
            notice.delete()
            self.__node.awaiting_renumber = False
          else:
            self.__node.awaiting_renumber = True
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

