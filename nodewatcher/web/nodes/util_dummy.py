from django.db import models, connection
from django.db.models.sql.constants import LOOKUP_SEP
from django.conf import settings
from web.nodes import ipcalc

# Quote name
qn = connection.ops.quote_name

class IPQuerySet(models.query.QuerySet):
  """
  A dumb query set that performs slow IP lookups for non-PostgreSQL
  databases.
  """
  def ip_filter(self, **kwargs):
    """
    Performs a slow IP lookup.
    """
    pks = []
    
    for key, value in kwargs.iteritems():
      field, op = key.split(LOOKUP_SEP)
      
      if op == 'contains':
        for obj in self.all():
          ip_range = ipcalc.Network(getattr(obj, field))
          if ipcalc.IP(value) in ip_range:
            pks.append(obj.pk)
        
        return self.filter(pk__in = pks)
      elif op == 'contained_in':
        for obj in self.all():
          ip_range = ipcalc.Network(getattr(obj, field))
          if ip_range in ipcalc.Network(value):
            pks.append(obj.pk)
        
        return self.filter(pk__in = pks)
      elif op == 'conflicts':
        for obj in self.all():
          ip_range = ipcalc.Network(getattr(obj, field))
          if ip_range in ipcalc.Network(value) or ipcalc.IP(value) in ip_range:
            pks.append(obj.pk)
        
        return self.filter(pk__in = pks)
      else:
        raise TypeError('Operation %s not supported.' % op)

class IPManager(models.Manager):
  """
  A dummy manager that emulates fast IP4 operations using slow linear
  lookups on non-PostgreSQL backends.
  """
  def get_query_set(self):
    """
    Returns a dummy query set.
    """
    return IPQuerySet(self.model)
  
  def ip_filter(self, *args, **kwargs):
    """
    Shortcut for queryset's ip_filter.
    """
    return self.get_query_set().ip_filter(*args, **kwargs)

class IPField(models.Field):
  """
  A dummy IP field.
  """
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    kwargs['max_length'] = 40
    super(IPField, self).__init__(*args, **kwargs)
  
  def get_internal_type(self):
    """
    Returns the internal type for this field.
    """
    return 'CharField'
  
  def get_db_prep_value(self, value):
    """
    Properly formats a value for this field.
    """
    try:
      ipcalc.IP(value)
    except ValueError:
      raise ValueError('Field %s requires a valid IP address!' % self.column)
    
    return value
  
  def get_db_prep_lookup(self, lookup_type, value):
    """
    Prepares this field for a database lookup.
    """
    if lookup_type != 'exact':
      raise TypeError('Lookup type %s not supported.' % lookup_type)
    
    return [self.get_db_prep_value(value)]

