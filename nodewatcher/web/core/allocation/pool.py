from django.db import models

# TODO locker should be moved somewhere else, possibly core.utils
from web.nodes.locker import require_lock
# TODO ipcalc should be moved somewhere else, possibly core.ipcalc
from web.nodes import ipcalc
# TODO ip fields should be moved somewhere else, possibly core.allocation.fields
from web.nodes.util import IPField, IPManager, queryset_by_ip

class PoolAllocationError(Exception):
  pass

class PoolFamily:
  """
  Possible address families.
  """
  Ipv4 = 4
  Ipv6 = 6

class PoolStatus:
  """
  Possible pools states.
  """
  Free = 0
  Full = 1
  Partial = 2

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
  status = models.IntegerField(default = PoolStatus.Free)
  description = models.CharField(max_length = 200, null = True)
  default_prefix_len = models.IntegerField(null = True)
  min_prefix_len = models.IntegerField(default = 24, null = True)
  max_prefix_len = models.IntegerField(default = 28, null = True)
  
  # Field for indexed lookups
  ip_subnet = IPField(null = True)
  
  # Custom manager
  objects = IPManager()
  
  class Meta:
    app_label = "core"
  
  def save(self, **kwargs):
    """
    Saves the model.
    """
    self.ip_subnet = '%s/%s' % (self.network, self.cidr)
    super(Pool, self).save(**kwargs)
  
  def split(self):
    """
    Splits this pool into two subpools.
    """
    net = ipcalc.Network(self.network, self.cidr)
    net0 = "%s/%d" % (self.network, self.cidr + 1)
    net1 = str(ipcalc.Network(long(net) + ipcalc.Network(net0).size())) 
    
    left = Pool(parent = self, family = self.family, network = self.network, cidr = self.cidr + 1)
    right = Pool(parent = self, family = self.family, network = net1, cidr = self.cidr + 1)
    left.save()
    right.save()
    
    self.status = PoolStatus.Partial
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
    
    if network == self.network and self.cidr == prefix_len and self.status == PoolStatus.Free:
      # We are the network, mark as full and save
      if not check_only:
        self.status = PoolStatus.Full
        self.save()
        return self
      else:
        return True
    
    # Find the proper network between our children
    alloc = None
    if self.children.count() > 0:
      for child in self.children.exclude(status = PoolStatus.Full):
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = PoolStatus.Full).count() == 2 and not check_only:
        self.status = PoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves
      for child in self.split():
        alloc = child.reserve_subnet(network, prefix_len, check_only)
        if alloc:
          break
      
      if not alloc or check_only:
        # Nothing has been allocated, this means that the given subnet
        # was invalid. Remove all children and become free again.
        self.children.all().delete()
        self.status = PoolStatus.Free
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
    
    if prefix_len == self.cidr and self.status == PoolStatus.Free:
      # We have found a free pool of the proper size, use it
      self.status = PoolStatus.Full
      self.save()
      return self
    
    # Pool not found, check if we have children - if we don't we'll have to split
    # and traverse the left one
    alloc = None
    if self.children.count() > 0:
      for child in queryset_by_ip(self.children.exclude(status = PoolStatus.Full), "ip_subnet"):
        alloc = child.allocate_buddy(prefix_len)
        if alloc:
          break
      else:
        return None
      
      # Something has been allocated, update our status
      if self.children.filter(status = PoolStatus.Full).count() == 2:
        self.status = PoolStatus.Full
        self.save()
    else:
      # Split ourselves into two halves and traverse the left half
      left, right = self.split()
      alloc = left.allocate_buddy(prefix_len)
    
    return alloc
  
  def reclaim_pools(self):
    """
    Coalesces free children back into one if possible.
    """
    if self.status == PoolStatus.Free:
      return self.parent.reclaim_pools() if self.parent else None
    
    # When all children are free, we don't need them anymore; when only some
    # are free, we mark this pool as partially free
    free_children = self.children.filter(status = PoolStatus.Free).count()
    if  free_children == 2:
      self.children.all().delete()
      self.status = PoolStatus.Free
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    elif free_children == 1:
      self.status = PoolStatus.Partial
      self.save()
      return self.parent.reclaim_pools() if self.parent else None
    else:
      # If any of the children are partial, we are partial as well
      if self.children.filter(status = PoolStatus.Partial).count() > 0:
        self.status = PoolStatus.Partial
        self.save()
        return self.parent.reclaim_pools() if self.parent else None 

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
    return Pool.objects.ip_filter(ip_subnet__conflicts = "%s/%s" % (network, cidr)).count() > 0
  
  def family_as_string(self):
    """
    Returns this pool's address family as a string.
    """
    if self.family == PoolFamily.Ipv4:
      return "IPv4"
    elif self.family == PoolFamily.Ipv6:
      return "IPv6"
    else:
      return _("unknown")

  def __unicode__(self):
    """
    Returns a string representation of this pool.
    """
    if self.description:
      return u"%s [%s/%d]" % (self.description, self.network, self.cidr)
    else: 
      return u"%s/%d" % (self.network, self.cidr)
  
  @require_lock('core_pool')
  def allocate_subnet(self, prefix_len = None):
    """
    Attempts to allocate a subnet from this pool.

    @param prefix_len: Wanted prefix length
    @return: A valid Pool instance of the allocated subpool
    """
    if not prefix_len:
      prefix_len = self.default_prefix_len
    
    if prefix_len < self.min_prefix_len or prefix_len > self.max_prefix_len:
      return None
    
    if prefix_len == 31:
      return None
    
    pool = self.allocate_buddy(prefix_len)
    return pool

