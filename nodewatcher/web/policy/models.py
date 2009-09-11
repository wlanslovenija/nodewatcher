from django.db import models
from wlanlj.nodes.models import Node
from datetime import datetime

class PolicyAction:
  """
  Valid policy actions.
  """
  NoAction = 0
  Shape = 1
  Drop = 2

class PolicyFamily:
  """
  Address families.
  """
  Ethernet = 1
  IPv4 = 4
  IPv6 = 6

class PolicyJob(models.Model):
  """
  An instruction to the policy daemon to update its policy for a
  specific IP address.
  """
  family = models.IntegerField()
  node = models.CharField(max_length = 40)
  addr = models.CharField(max_length = 40)
  created_at = models.DateTimeField()

  @staticmethod
  def add(node, family, addr):
    """
    A helper method for adding a new job.
    """
    j = PolicyJob()
    j.node = node
    j.family = family
    j.addr = addr
    j.created_at = datetime.now()
    j.save()

class TrafficControlClass(models.Model):
  """
  A traffic control class.
  """
  bandwidth = models.IntegerField()

  def __unicode__(self):
    """
    Returns a string representation of this model.
    """
    return "%d kbit/s" % self.bandwidth

class Policy(models.Model):
  """
  A model representing an egress policy.
  """
  node = models.ForeignKey(Node, related_name = 'gw_policy')
  addr = models.CharField(max_length = 40)
  family = models.IntegerField()
  action = models.IntegerField()
  last_updated = models.DateTimeField()
  tc_class = models.ForeignKey(TrafficControlClass)
  
  @staticmethod
  def set_policy(node, addr, action, tc_class, family = PolicyFamily.IPv4):
    """
    A helper method for adding a new policy entry (or updating an
    existing one).
    
    @param node: Node that holds the policy
    @param addr: Destination address
    @param action: Policy action
    @param tc_class: Traffic control class
    @param family: Optional address family specifier
    """
    try:
      p = Policy.objects.get(node = node, addr = addr)
    except Policy.DoesNotExist:
      p = Policy(node = node, addr = addr)

    p.action = action
    p.tc_class = tc_class
    p.family = family
    p.last_updated = datetime.now()
    p.save()

    # Add an update job, just to be sure
    PolicyJob.add(node.ip, family, addr)
  
  def delete(self):
    """
    Removes this policy.
    """
    node, family, addr = self.node, self.family, self.addr
    super(Policy, self).delete()

    # Add an update job, so this gets properly removed
    PolicyJob.add(node.ip, family, addr)

