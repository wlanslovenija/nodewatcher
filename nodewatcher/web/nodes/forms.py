from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from ljwifi.nodes.models import Project, Pool, NodeStatus, Node, Subnet, SubnetStatus, AntennaType, PolarizationType
from ljwifi.nodes import ipcalc
from ljwifi.generator.models import Template, Profile
from ljwifi.generator.types import IfaceType
from ljwifi.account.util import generate_random_password
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

class RegisterNodeForm(forms.Form):
  """
  A simple form for new node registration.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"))
  ip = forms.CharField(max_length = 40, required = False, label = _("IP address"))
  location = forms.CharField(max_length = 200)
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))

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
  
  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False)
  border_router = forms.BooleanField(required = False)

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all(),
    label = _("Router type")
  )
  root_pass = forms.CharField(required = False)
  use_vpn = forms.BooleanField(required = False, initial = True,
    label = _("Enable VPN"),
  )
  use_captive_portal = forms.BooleanField(required = False, initial = True,
    label = _("Enable captive portal")
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

  def clean(self):
    """
    Additional validation handler.
    """
    ip = self.cleaned_data.get('ip')

    if ip and not IPV4_ADDR_RE.match(ip) or ip.startswith('127.'):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))

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
    node.name = self.cleaned_data.get('name')
    node.project = project
    node.owner = user
    node.location = self.cleaned_data.get('location')
    node.geo_lat = self.cleaned_data.get('geo_lat')
    node.geo_long = self.cleaned_data.get('geo_long')
    node.ant_external = self.cleaned_data.get('ant_external')
    node.ant_polarization = self.cleaned_data.get('ant_polarization')
    node.ant_type = self.cleaned_data.get('ant_type')

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.status = NodeStatus.New
    node.save()

    # Create node profile for image generator
    profile = Profile(node = node, template = self.cleaned_data.get('template'))
    profile.root_pass = self.cleaned_data.get('root_pass') or generate_random_password(8)
    profile.use_vpn = self.cleaned_data.get('use_vpn')
    profile.use_captive_portal = self.cleaned_data.get('use_captive_portal')
    profile.save()

    if subnet:
      subnet.save()

    return node

class UpdateNodeForm(forms.Form):
  """
  A simple form for updating node information.
  """
  name = forms.CharField(max_length = 50, label = _("Node name"))
  ip = forms.CharField(max_length = 40, label = _("IP address"))
  location = forms.CharField(max_length = 200)
  geo_lat = forms.FloatField(required = False, label = _("Lattitude"))
  geo_long = forms.FloatField(required = False, label = _("Longitude"))
  owner = forms.ModelChoiceField(
    User.objects.all(),
    initial = User.objects.all()[0].id,
    label = _("Owner")
  )

  # Special node properties (can only be set by staff)
  system_node = forms.BooleanField(required = False)
  border_router = forms.BooleanField(required = False)

  # Image generator stuff
  template = forms.ModelChoiceField(
    Template.objects.all(),
    label = _("Router type")
  )
  root_pass = forms.CharField()
  use_vpn = forms.BooleanField(required = False,
    label = _("Enable VPN"),
  )
  use_captive_portal = forms.BooleanField(required = False,
    label = _("Enable captive portal")
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

  def clean(self):
    """
    Additional validation handler.
    """
    ip = self.cleaned_data.get('ip')

    if ip and not IPV4_ADDR_RE.match(ip) or ip.startswith('127.'):
      raise forms.ValidationError(_("The IP address you have entered is invalid!"))

    return self.cleaned_data
  
  def save(self, node, user):
    """
    Completes node data update.
    """
    ip = self.cleaned_data.get('ip')

    # Update node metadata
    node.name = self.cleaned_data.get('name')
    node.owner = self.cleaned_data.get('owner')
    node.location = self.cleaned_data.get('location')
    node.geo_lat = self.cleaned_data.get('geo_lat')
    node.geo_long = self.cleaned_data.get('geo_long')
    node.ant_external = self.cleaned_data.get('ant_external')
    node.ant_polarization = self.cleaned_data.get('ant_polarization')
    node.ant_type = self.cleaned_data.get('ant_type')

    if user.is_staff:
      node.system_node = self.cleaned_data.get('system_node')
      node.border_router = self.cleaned_data.get('border_router')
    
    node.save()

    # Update node profile for image generator
    profile = node.profile
    profile.template = self.cleaned_data.get('template')
    profile.root_pass = self.cleaned_data.get('root_pass')
    profile.use_vpn = self.cleaned_data.get('use_vpn')
    profile.use_captive_portal = self.cleaned_data.get('use_captive_portal')
    profile.save()

class AllocateSubnetForm(forms.Form):
  """
  A simple form for subnet allocation.
  """
  network = forms.CharField(max_length = 50, required = False)
  description = forms.CharField(max_length = 200)
  iface_type = forms.ChoiceField(
    choices = [
      (IfaceType.WiFi, 'WiFi'),
      (IfaceType.LAN, 'LAN'),
      (IfaceType.WAN, 'WAN')
    ],
    initial = IfaceType.LAN,
    label = _("Interface")
  )
  dhcp = forms.BooleanField(required = False, initial = True, label = _("DHCP announce"))
  
  def clean(self):
    """
    Additional validation handler.
    """
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

