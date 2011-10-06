import datetime

from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import ugettext as _

from web.core.allocation import pool as pool_models
# TODO project model should be moved to core
from web.nodes import models as nodes_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration

class AddressAllocator(models.Model):
  """
  An abstract class defining an API for address allocator items.
  """
  class Meta:
    abstract = True
  
  usage = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#usage")
  
  def exactly_matches(self, other):
    """
    Returns true if this allocation request exactly matches the other. This
    should only return true if both requests share the same allocated
    resource.
    """
    raise NotImplementedError
  
  def is_satisfied(self):
    """
    Returns true if this allocation request is satisfied.
    """
    raise NotImplementedError
  
  def satisfy(self, obj):
    """
    Attempts to satisfy this allocation request by obtaining a new allocation
    for the specified object.
    
    @param obj: A valid Django model instance
    """
    raise NotImplementedError
  
  def satisfy_from(self, other):
    """
    Attempts to satisfy this request by taking resources from an existing one.
    
    @param other: AddressAllocator instance
    @return: True if request has been satisfied, False otherwise
    """
    raise NotImplementedError
  
  def free(self):
    """
    Frees this allocation.
    """
    raise NotImplementedError

class IpAddressAllocator(AddressAllocator):
  """
  An abstract class defining an API for IP address allocator items.
  """
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#ip_family")
  pool = registry_fields.ModelSelectorKeyField(pool_models.IpPool, limit_choices_to = { 'parent' : None })
  prefix_length = models.IntegerField(default = 27)
  allocation = models.ForeignKey(pool_models.IpPool, editable = False, null = True,
    on_delete = models.PROTECT, related_name = 'allocations_%(app_label)s_%(class)s')
  
  class Meta:
    abstract = True
  
  def exactly_matches(self, other):
    """
    Returns true if this allocation request exactly matches the other. This
    should only return true if both requests share the same allocated
    resource.
    """
    if not self.is_satisfied() or not other.is_satisfied():
      return False
    
    return self.allocation == other.allocation
  
  def satisfy_from(self, other):
    """
    Attempts to satisfy this request by taking resources from an existing one.
    
    @param other: AddressAllocator instance
    @return: True if request has been satisfied, False otherwise
    """
    if not other.is_satisfied():
      return False
    
    if other.family != self.family:
      return False
    
    if other.prefix_length != self.prefix_length:
      return False
    
    if other.pool != self.pool:
      return False
    
    self.allocation = other.allocation
    self.save()
    return True
  
  def is_satisfied(self):
    """
    Returns true if this allocation request is satisfied.
    """
    if self.allocation is None:
      return False
    
    if self.allocation.family != self.family:
      return False
    
    if self.allocation.prefix_length != self.prefix_length:
      return False
    
    if self.allocation.top_level() != self.pool:
      return False
    
    return True
  
  def satisfy(self, obj):
    """
    Attempts to satisfy this allocation request by obtaining a new allocation
    for the specified object.
    
    @param obj: A valid Django model instance
    """
    self.allocation = self.pool.allocate_subnet(self.prefix_length)
    
    if self.allocation is not None:
      self.allocation.allocation_content_object = obj
      self.allocation.allocation_timestamp = datetime.datetime.now()
      self.allocation.save()
      self.save()
    else:
      raise registry_forms.RegistryValidationError(
        _(u"Unable to satisfy address allocation request for /%(prefix)s from '%(pool)s'!") % {
          'prefix' : self.prefix_length, 'pool' : unicode(self.pool)
        }
      )
  
  def free(self):
    """
    Frees this allocation.
    """
    if self.allocation is None:
      return
    
    self.allocation.free()
    self.allocation = None
    self.save()

class IpAddressAllocatorFormMixin(object):
  """
  A mixin for address allocator forms.
  """
  def modify_to_context(self, item, cfg):
    """
    Dynamically modifies the form.
    """
    # Only display pools that are available to the selected project
    qs = self.fields['pool'].queryset
    try:
      qs = qs.filter(projects = cfg['core.project'][0].project)
      qs = qs.filter(family = item.family)
      qs = qs.order_by("description", "ip_subnet")
    except (nodes_models.Project.DoesNotExist, KeyError, AttributeError):
      qs = qs.none()
    
    self.fields['pool'].queryset = qs
    
    # Only display prefix length range that is available for the selected pool
    try:
      pool = item.pool
      self.fields['prefix_length'] = registry_fields.SelectorFormField(
        label = _("Prefix Length"),
        choices = BLANK_CHOICE_DASH + [
          (plen, "/%s" % plen)
          for plen in xrange(pool.prefix_length_minimum, pool.prefix_length_maximum + 1)
        ],
        initial = pool.prefix_length_default,
        coerce = int,
        empty_value = None
      )
    except (pool_models.IpPool.DoesNotExist, AttributeError):
      self.fields['prefix_length'] = registry_fields.SelectorFormField(label = _("Prefix Length"), choices = BLANK_CHOICE_DASH)

