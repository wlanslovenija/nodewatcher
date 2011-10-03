from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models

from web.registry import fields as registry_fields
from web.utils import ipcalc, db_locker
import fields as allocation_fields

class PoolAllocationError(Exception):
  pass

class IpPoolStatus:
  """
  Possible pools states.
  """
  Free = 0
  Full = 1
  Partial = 2

class PoolBase(models.Model):
  """
  An abstract base class for all pool implementations.
  """
  class Meta:
    abstract = True
  
  parent = models.ForeignKey('self', null = True, related_name = 'children')
  projects = models.ManyToManyField("nodes.Project", related_name = 'pools_%(app_label)s_%(class)s')
  
  # Bookkeeping for allocated pools
  alloc_content_type = models.ForeignKey(ContentType, null = True)
  alloc_object_id = models.CharField(max_length = 50, null = True)
  alloc_content_object = generic.GenericForeignKey('alloc_content_type', 'alloc_object_id')
  alloc_timestamp = models.DateTimeField(null = True)
  
  def top_level(self):
    """
    Returns the root of this pool tree.
    """
    if self.parent:
      return self.parent.top_level()
    
    return self
  
  def free(self):
    """
    Frees this allocated item and returns it to the parent pool.
    """
    raise NotImplementedError

class IpPool(PoolBase):
  """
  This class represents an IP pool - that is a subnet available for
  allocation purpuses. Every IP block that is allocated is represented
  as an IpPool instance with proper parent pool reference.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#family")
  network = models.CharField(max_length = 50)
  cidr = models.IntegerField()
  status = models.IntegerField(default = IpPoolStatus.Free)
  description = models.CharField(max_length = 200, null = True)
  default_prefix_len = models.IntegerField(null = True)
  min_prefix_len = models.IntegerField(default = 24, null = True)
  max_prefix_len = models.IntegerField(default = 28, null = True)
  
  # Field for indexed lookups
  ip_subnet = allocation_fields.IPField(null = True)
  
  # Custom manager
  objects = allocation_fields.IPManager()
  
  class Meta:
    app_label = "core"
  
  def save(self, **kwargs):
    """
    Saves the model.
    """
    self.ip_subnet = '%s/%s' % (self.network, self.cidr)
    super(IpPool, self).save(**kwargs)
  
  def split_buddy(self):
    """
    Splits this pool into two subpools.
    """
    net = ipcalc.Network(self.network, self.cidr)
    net0 = "%s/%d" % (self.network, self.cidr + 1)
    net1 = str(ipcalc.Network(long(net) + ipcalc.Network(net0).size())) 
    
    left = IpPool(parent = self, family = self.family, network = self.network, cidr = self.cidr + 1)
    right = IpPool(parent = self, family = self.family, network = net1, cidr = self.cidr + 1)
    left.save()
    right.save()
    
    self.status = IpPoolStatus.Partial
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
    
    if network == self.network and self.cidr == prefix_len and self.status == IpPoolStatus.Free:
      # We are the network, mark as full and save
      if not check_only:
        self.status = IpPoolStatus.Full
        self.save()
        return self
      else:
        return True
    
    # Find the proper network between our children
    alloc = None
    if self.children.count() > 0:
      for child in self.children.exclude(status = IpPoolStatus.Full):
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = IpPoolStatus.Full).count() == 2 and not check_only:
        self.status = IpPoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves
      for child in self.split_buddy():
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      
      if not alloc or check_only:
        # Nothing has been allocated, this means that the given subnet
        # was invalid. Remove all children and become free again.
        self.children.all().delete()
        self.status = IpPoolStatus.Free
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
    
    if prefix_len == self.cidr and self.status == IpPoolStatus.Free:
      # We have found a free pool of the proper size, use it
      self.status = IpPoolStatus.Full
      self.save()
      return self
    
    # Pool not found, check if we have children - if we don't we'll have to split
    # and traverse the left one
    alloc = None
    if self.children.count() > 0:
      for child in self.children.exclude(status = IpPoolStatus.Full).order_by("ip_subnet"):
        alloc = child.allocate_buddy(prefix_len)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = IpPoolStatus.Full).count() == 2:
        self.status = IpPoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves and traverse the left half
      left, right = self.split_buddy()
      alloc = left.allocate_buddy(prefix_len)
    
    return alloc
  
  def reclaim_pools(self):
    """
    Coalesces free children back into one if possible.
    """
    if self.status == IpPoolStatus.Free:
      return self.parent.reclaim_pools() if self.parent else None
    
    # When all children are free, we don't need them anymore; when only some
    # are free, we mark this pool as partially free
    free_children = self.children.filter(status = IpPoolStatus.Free).count()
    if  free_children == 2:
      self.children.all().delete()
      self.status = IpPoolStatus.Free
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    elif free_children == 1:
      self.status = IpPoolStatus.Partial
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    else:
      # If any of the children are partial, we are partial as well
      if self.children.filter(status = IpPoolStatus.Partial).count() > 0:
        self.status = IpPoolStatus.Partial
        self.save()
        return self.parent.reclaim_pools() if self.parent else None 
  
  def free(self):
    """
    Frees this allocated item and returns it to the parent pool.
    """
    self.status = IpPoolStatus.Free
    self.alloc_content_object = None
    self.alloc_timestamp = None
    self.save()
    self.reclaim_pools()
  
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
    return IpPool.objects.ip_filter(ip_subnet__conflicts = "%s/%s" % (network, cidr)).count() > 0
  
  def family_as_string(self):
    """
    Returns this pool's address family as a string.
    """
    for enum, desc in self._meta.get_field_by_name("family")[0].choices:
      if enum == self.family:
        return desc
    
    return _("unknown")

  def __unicode__(self):
    """
    Returns a string representation of this pool.
    """
    if self.description:
      return u"%s [%s/%d]" % (self.description, self.network, self.cidr)
    else: 
      return u"%s/%d" % (self.network, self.cidr)
  
  @db_locker.require_lock('core_pool')
  def allocate_subnet(self, prefix_len = None):
    """
    Attempts to allocate a subnet from this pool.

    @param prefix_len: Wanted prefix length
    @return: A valid IpPool instance of the allocated subpool
    """
    if not prefix_len:
      prefix_len = self.default_prefix_len
    
    if prefix_len < self.min_prefix_len or prefix_len > self.max_prefix_len:
      return None
    
    if prefix_len == 31:
      return None
    
    pool = self.allocate_buddy(prefix_len)
    return pool

