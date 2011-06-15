from datetime import datetime
import re

from django import forms
from django.forms import widgets
from django.db import transaction, models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core import validators as core_validators
from django.conf import settings

from web.core.allocation import pool as pool_models
from web.nodes.models import Project, NodeStatus, Node, Subnet, SubnetStatus, AntennaType, PolarizationType, WhitelistItem, EventCode, EventSubscription, NodeType, Event, EventSource, SubscriptionType, Link, RenumberNotice, GraphType, NodeNames
from web.nodes.sticker import generate_sticker
from web.nodes.transitions import validates_node_configuration
from web.nodes.common import FormWithWarnings
from web.generator.models import Template, Profile, OptionalPackage, gen_mac_address
from web.generator.types import IfaceType
from web.account.util import generate_random_password
from web.dns.models import Record
from web.policy.models import TrafficControlClass, Policy, PolicyFamily, PolicyAction
from web.utils import ipcalc

IPV4_ADDR_RE = re.compile(r'^\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b$')
MAC_ADDR_RE = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
MAC_ADDR_RE_ALT = re.compile(r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$') # Windows displays MAC address as physical address with dashes

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
      node.project.pools.exclude(status = pool_models.PoolStatus.Full).filter(parent = None).order_by('description', 'ip_subnet'),
      empty_label = None,
      label = _("IP pool"),
      initial = primary_pool.pk if primary_pool else 0
    )
  
  def get_pools(self):
    """
    A helper method that returns the IP pools.
    """
    return self.__node.project.pools.exclude(status = pool_models.PoolStatus.Full).filter(parent = None).order_by('description', 'ip_subnet')
  
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
      if pool_models.Pool.contains_network(network, cidr):
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
    
    for subnet in node.subnet_set.filter(allocated = True).order_by('ip_subnet'):
      pools = []
      for pool in node.project.pools.exclude(status = pool_models.PoolStatus.Full).order_by('description', 'ip_subnet'):
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
    return self.__node.project.pools.exclude(status = pool_models.PoolStatus.Full).order_by('description', 'ip_subnet')
  
  def get_subnet_fields(self):
    """
    A helper method that returns all subnet fields in order.
    """
    for subnet in self.__node.subnet_set.filter(allocated = True).order_by('ip_subnet'):
      field = self['subnet_%s' % subnet.pk]
      field.model = subnet
      field.prefix = 'prefix_%s' % subnet.pk
      field.manual_ip = self['manual_%s' % subnet.pk]
      yield field
  
  def clean(self):
    """
    Additional validation handler.
    """
    for subnet in self.__node.subnet_set.filter(allocated = True).order_by('ip_subnet'):
      manual_ip = self.cleaned_data.get('manual_%s' % subnet.pk)
      if not manual_ip:
        continue
      
      action = int(self.cleaned_data.get('subnet_%s' % subnet.pk))
      prefix_len = int(self.cleaned_data.get('prefix_%s' % subnet.pk) or 27)
      
      # Validate IP address format
      if not IPV4_ADDR_RE.match(manual_ip):
        raise forms.ValidationError(_("Enter a valid IP address or leave the subnet field empty!"))
      
      # Validate pool status
      pool = pool_models.Pool.objects.get(pk = action)
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
    for subnet in self.__node.subnet_set.filter(allocated = True).order_by('ip_subnet')[:]:
      action = int(self.cleaned_data.get('subnet_%s' % subnet.pk))
      prefix_len = int(self.cleaned_data.get('prefix_%s' % subnet.pk) or 27)
      manual_ip = self.cleaned_data.get('manual_%s' % subnet.pk)
      
      if action == RenumberAction.Keep:
        pass
      elif action == RenumberAction.Remove:
        subnet.delete()
      else:
        # This means we should renumber to some other pool
        pool = pool_models.Pool.objects.get(pk = action)
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

