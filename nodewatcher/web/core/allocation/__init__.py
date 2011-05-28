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
  family = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#family")
  pool = registry_fields.ModelSelectorKeyField(pool_models.Pool, limit_choices_to = { 'parent' : None })
  cidr = models.IntegerField(default = 27)
  usage = registry_fields.SelectorKeyField("node.config", "core.interfaces.network#usage")
  
  class Meta:
    abstract = True
  
  def is_satisfied_by(self, allocation):
    """
    Returns true if the given allocation satisfies this allocation request.
    
    @param allocation: A valid Allocation instance
    """
    if allocation.pool.cidr != self.cidr:
      return False
    
    if allocation.pool.family != self.family:
      return False
    
    if allocation.pool.top_level() != self.pool:
      return False
    
    return True
  
  def satisfy(self, obj):
    """
    Attempts to satisfy this allocation request by obtaining a new allocation
    for the specified object.
    
    @param obj: A valid Django model instance
    """
    allocation = pool_models.Allocation(
      content_object = obj,
      pool = self.pool.allocate_subnet(self.cidr)
    )
    
    if allocation.pool is not None:
      allocation.save()
    else:
      raise registry_forms.RegistryValidationError(
        _(u"Unable to satisfy address allocation request for /%(prefix)s from '%(pool)s'!") % {
          'prefix' : self.cidr, 'pool' : unicode(self.pool)
        }
      )

class AddressAllocatorFormMixin(object):
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
      qs = qs.filter(projects = cfg['core.general'][0].project)
      qs = qs.filter(family = item.family)
      qs = qs.order_by("description", "ip_subnet")
    except nodes_models.Project.DoesNotExist:
      qs = qs.none()
    
    self.fields['pool'].queryset = qs
    
    # Only display CIDR range that is available for the selected pool
    try:
      pool = item.pool
      self.fields['cidr'] = registry_fields.SelectorFormField(
        label = "CIDR",
        choices = BLANK_CHOICE_DASH + [(plen, "/%s" % plen) for plen in xrange(pool.min_prefix_len, pool.max_prefix_len + 1)],
        initial = pool.default_prefix_len,
        coerce = int,
        empty_value = None
      )
    except pool_models.Pool.DoesNotExist:
      self.fields['cidr'] = registry_fields.SelectorFormField(label = "CIDR", choices = BLANK_CHOICE_DASH)

