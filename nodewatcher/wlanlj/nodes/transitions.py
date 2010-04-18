from django.utils.translation import ugettext as _
from django.db import transaction
from django.core.exceptions import ImproperlyConfigured
from django import forms
from wlanlj.generator.types import IfaceType

class AdaptationFailed(Exception):
  reason = _("Unknown")
  
  def __init__(self, reason):
    """
    Class constructor.
    """
    self.reason = reason

class RouterTransition(object):
  """
  An abstract router transition.
  """
  def adapt(self, node):
    """
    Adapts current node configuration in accordance with this
    transition specification.
    
    @param node: Node configuration to be adapted
    """
    raise NotImplementedError

def validates_node_configuration(f):
  """
  A decorator for convenience.
  """
  from wlanlj.nodes.models import Node
  
  def _fun(self, *args, **kwargs):
    try:
      # Create a savepoint since we might rollback if later on we discover that
      # this configuration is not possible due to adaptation chain failure
      sid = transaction.savepoint()
      
      # Execute our function
      node = f(self, *args, **kwargs)
      if not isinstance(node, Node):
        raise ImproperlyConfigured(_("Improper use of validates_node_configuration decorator! Decorated function must return a Node instance."))
      
      # Validate adaptation chain
      try:
        node.adapt_to_router_type()
      except AdaptationFailed, e:
        transaction.savepoint_rollback(sid)
        error = forms.ValidationError(e.reason)
        self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class(error.messages)
        return False
        
      # Validation ok, let's commit
      transaction.savepoint_commit(sid)
    except:
      transaction.savepoint_rollback(sid)
      raise
    
    return True
  
  return _fun    

#
# Actual router transition classes
#

class OneWiFiSubnet(RouterTransition):
  """
  Ensures that the specified node configuration only has a single
  WiFi subnet allocated.
  """
  def adapt(self, node):
    """
    Adapts current node configuration in accordance with this
    transition specification.
    
    @param node: Node configuration to be adapted
    """
    if node.subnet_set.filter(allocated = True, gen_iface_type = IfaceType.WiFi).count() > 1:
      raise AdaptationFailed(_("Only one WiFi subnet may be allocated to the specified router!"))

class OnePortVPN(RouterTransition):
  """
  Ensures that the specified node configuration has either no
  VPN enabled or no subnets on the LAN port. This is meant for
  routers that only have one Ethernet port and its role is decided
  between WAN/LAN.
  """
  def adapt(self, node):
    """
    Adapts current node configuration in accordance with this
    transition specification.
    
    @param node: Node configuration to be adapted
    """
    if node.profile.use_vpn and node.has_allocated_subnets(IfaceType.LAN):
      raise AdaptationFailed(_("The specified router only has one ethernet port! VPN and any LAN subnet are mutually exclusive!"))

