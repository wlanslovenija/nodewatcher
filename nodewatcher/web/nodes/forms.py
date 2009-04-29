from django import forms
from django.forms import widgets
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from wlanlj.nodes.models import Project, Pool, NodeStatus, Node, Subnet, SubnetStatus, AntennaType, PolarizationType, WhitelistItem, EventCode, EventSubscription, NodeType, Event, EventSource
from wlanlj.nodes import ipcalc
from wlanlj.nodes.sticker import generate_sticker
from wlanlj.generator.models import Template, Profile
from wlanlj.generator.types import IfaceType
from wlanlj.account.util import generate_random_password
from wlanlj.dns.models import Record
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
MAC_ADDR_RE = re.compile(r'([0-9A-Fa-f]{2}([:]|$)){6}')
NODE_NAME_RE = re.compile('(?:[a-zA-Z0-9]+-?[a-zA-Z0-9]*)*[a-zA-Z0-9]$')

class RegisterNodeForm(forms.Form):
  """
  A simple form for new node registration.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"))
  ip = forms.CharField(max_length = 40, required = False, label = _("IP address"))
  location = forms.CharField(max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea)
  url = forms.CharField(max_length = 200, required = False, label = _("Info URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

  # Additional flags
  assign_ip = forms.BooleanField(required = False, label = _("No IP yet? Assign me one!"), initial = True)
  assign_subnet = forms.BooleanField(required = False, initial = True,
    label = _("Assign a new subnet")
  )
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = Project.objects.all()[0].id,
    label = _("Project")
  )
  node_type = forms.ChoiceField(
    choices = [
      (NodeType.Mesh, _("Mesh node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node"))
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

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may only contain letters, numbers and hyphens!"))

    if (geo_lat or geo_long) and (not (45 <= geo_lat <= 47) or not (13 <= geo_long <= 17)):
      raise forms.ValidationError(_("The specified latitude/longitude are out of range!"))

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

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.status = NodeStatus.New
    node.save()

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
      profile.save()

    if subnet:
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
  location = forms.CharField(max_length = 200, widget = widgets.TextInput(attrs = {'size': '40'}))
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  owner = forms.ModelChoiceField(
    User.objects.all(),
    initial = User.objects.all()[0].id,
    label = _("Maintainer")
  )
  project = forms.ModelChoiceField(
    Project.objects.all(),
    initial = Project.objects.all()[0].id,
    label = _("Project")
  )
  node_type = forms.ChoiceField(
    choices = [
      (NodeType.Mesh, _("Mesh node")),
      (NodeType.Server, _("Server node")),
      (NodeType.Test, _("Test node"))
    ],
    initial = NodeType.Mesh,
    label = _("Node type")
  )
  notes = forms.CharField(max_length = 1000, required = False, label = _("Notes"), widget = widgets.Textarea)
  url = forms.CharField(max_length = 200, required = False, label = _("Info URL"), widget = widgets.TextInput(attrs = {'size': '40'}))

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

    try:
      if use_vpn and not template.iface_lan and node.has_allocated_subnets(IfaceType.LAN):
        raise forms.ValidationError(_("The specified router only has one ethernet port! You have already added some LAN subnets to it, so you cannot enable VPN!"))
    except Profile.DoesNotExist:
      pass

    if not NODE_NAME_RE.match(name):
      raise forms.ValidationError(_("The specified node name is not valid. A node name may only contain letters, numbers and hyphens!"))

    if (geo_lat or geo_long) and (not (45 <= geo_lat <= 47) or not (13 <= geo_long <= 17)):
      raise forms.ValidationError(_("The specified latitude/longitude are out of range!"))

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

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.save()

    # Update DNS records on name changes
    if oldName != node.name or oldProject != node.project:
      Record.update_for_node(node, old_name = oldName, old_project = oldProject)

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
      profile.save()
    elif profile:
      profile.delete()

class AllocateSubnetForm(forms.Form):
  """
  A simple form for subnet allocation.
  """
  network = forms.CharField(max_length = 50, required = False)
  description = forms.CharField(max_length = 200)
  iface_type = forms.ChoiceField(
    choices = [
      (IfaceType.WiFi, 'WiFi'),
      (IfaceType.LAN, 'LAN')
    ],
    initial = IfaceType.LAN,
    label = _("Interface")
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

      # Check if the given subnet is part of any allocation pools
      if Pool.contains_network(network, cidr):
        raise forms.ValidationError(_("Specified subnet is part of an allocation pool and cannot be manually allocated!"))

      self.cleaned_data['network'] = network
      self.cleaned_data['cidr'] = cidr

    return self.cleaned_data

  def save(self, node):
    """
    Completes subnet allocation.
    """
    if self.cleaned_data.get('network'):
      subnet = Subnet(node = node)
      subnet.subnet = self.cleaned_data.get('network')
      subnet.cidr = self.cleaned_data.get('cidr')
      subnet.allocated = True
      subnet.allocated_at = datetime.now()
      subnet.status = SubnetStatus.NotAnnounced
      subnet.description = self.cleaned_data.get('description')
      subnet.gen_iface_type = self.cleaned_data.get('iface_type')
      subnet.gen_dhcp = self.cleaned_data.get('dhcp')
      subnet.save()
    else:
      pool = node.project.pool
      allocation = pool.allocate_subnet()
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

class WhitelistMacForm(forms.Form):
  """
  A simple form for whitelisting a MAC address.
  """
  mac = forms.CharField(max_length = 17, label = _("MAC address"))
  
  def clean(self):
    """
    Additional validation handler.
    """
    mac = self.cleaned_data.get('mac')
    if not MAC_ADDR_RE.match(mac) or len(mac) != 17:
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
    initial = Project.objects.all()[0].id,
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
  node = forms.ModelChoiceField(
    Node.objects.exclude(status = NodeStatus.Invalid),
    label = _("Node"),
    required = False
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
      (EventCode.RedundancyLoss, _('Redundant link to border gateway has gone down'))
    ],
    required = False
  )

  def save(self, user):
    """
    Saves whitelist entry.
    """
    s = EventSubscription(user = user)
    s.node = self.cleaned_data.get('node') or None
    s.code = int(self.cleaned_data.get('code')) or None
    s.save()

