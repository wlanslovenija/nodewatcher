from django.contrib.gis.db import models as gis_models
from django.db import models, connection

from registry import access as registry_access

# Quote name
qn = connection.ops.quote_name

class RegistryQuerySet(gis_models.query.GeoQuerySet):
  """
  An augmented query set that enables lookups of values from the registry.
  """
  def regpoint(self, name):
    """
    Switches to a different regpoint that determines the short attribute
    name.
    """
    from registry import registration
    clone = self._clone()
    try:
      name = "{0}.{1}".format(self.model._meta.module_name, name)
      clone._regpoint = registration.point(name)
      return clone
    except KeyError:
      raise ValueError("Registration point '{0}' does not exist!".format(name))
  
  def filter(self, **kwargs):
    """
    An augmented filter that enables filtering by virtual aliases for
    registry fields via joins.
    """
    if not hasattr(self, "_regpoint"):
      return super(RegistryQuerySet, self).filter(**kwargs)
    
    clone = self._clone()
    
    # Resolve fields from kwargs that are virtual aliases for registry fields
    for condition, value in kwargs.items():
      if '__' in condition:
        field = condition[:condition.find('__')]
      else:
        field = condition
      
      dst_model, dst_field = self._regpoint.flat_lookup_proxies.get(field, (None, None))
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
        (self.model._meta.db_table, top_model._meta.db_table, self.model._meta.pk.column, 'root_id'),
        promote = True
      )
      
      if top_model != dst_model:
        # Join with lower-level item
        clone.query.join(
          (top_model._meta.db_table, dst_model._meta.db_table, top_model._meta.pk.column, dst_model._meta.pk.column),
          promote = True
        )
    
    return clone

class RegistryLookupManager(gis_models.GeoManager):
  """
  A manager for doing lookups over the registry models.
  """
  def __init__(self, regpoint = None):
    """
    Class constructor.
    
    @param regpoint: Registration point instance
    """
    self._regpoint = regpoint
    super(RegistryLookupManager, self).__init__()
  
  def get_query_set(self):
    qs = RegistryQuerySet(self.model, using = self._db)
    if self._regpoint is not None:
      qs._regpoint = self._regpoint
    return qs
  
  def regpoint(self, name):
    return self.get_query_set().regpoint(name)
  
  def registry_fields(self, **kwargs):
    return self.get_query_set().registry_fields(**kwargs)


