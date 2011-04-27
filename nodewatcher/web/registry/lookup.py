from django.db import models, connection

from registry import state as registry_state
from registry import access as registry_access

# Quote name
qn = connection.ops.quote_name

class RegistryQuerySet(models.query.QuerySet):
  """
  An augmented query set that enables lookups of values from the registry.
  """
  def filter(self, **kwargs):
    """
    An augmented filter that enables filtering by virtual aliases for
    registry fields via joins.
    """
    clone = self._clone()
    
    # Resolve fields from kwargs that are virtual aliases for registry fields
    for condition, value in kwargs.items():
      if '__' in condition:
        field = condition[:condition.find('__')]
      else:
        field = condition
      
      dst_model, dst_field = registry_state.FLAT_LOOKUP_PROXIES.get(field, (None, None))
      if dst_model is None and '_' in field:
        dst_model, dst_field = field.split('_', 1)
        try:
          dst_model = registry_access.get_model_class_by_name(dst_model)
        except:
          dst_model = None
      
      if dst_model is not None:
        dst_field = dst_model.lookup_path() + '__' + dst_field
        del kwargs[condition]
        condition = condition.replace(field, dst_field)
        kwargs[condition] = value
    
    # Pass transformed query into the standard filter routine
    return super(RegistryQuerySet, clone).filter(**kwargs)
  
  def registry_fields(self, **kwargs):
    """
    Select fields from the registry.
    """
    clone = self._clone()
    
    for field, dst in kwargs.iteritems():
      dst_model, dst_field = dst.split('.')
      dst_model = registry_access.get_model_class_by_name(dst_model)
      
      clone = clone.extra(select = { field : "%s.%s" % (qn(dst_model._meta.db_table), qn(dst_field)) })
      clone.query.get_initial_alias()
      
      # Join with top-level item
      top_model = dst_model.top_model()
      clone.query.join(
        (self.model._meta.db_table, top_model._meta.db_table, self.model._meta.pk.column, 'node_id'),
        promote = True
      )
      
      if top_model != dst_model:
        # Join with lower-level item
        clone.query.join(
          (top_model._meta.db_table, dst_model._meta.db_table, top_model._meta.pk.column, dst_model._meta.pk.column),
          promote = True
        )
    
    return clone

class RegistryLookupManager(models.Manager):
  """
  A manager for doing lookups over the registry models.
  """
  def get_query_set(self):
    return RegistryQuerySet(self.model)
  
  def registry_fields(self, **kwargs):
    return self.get_query_set().registry_fields(**kwargs)


