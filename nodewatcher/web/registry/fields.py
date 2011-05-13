import types

from django.core import exceptions
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import widgets
from django.utils.safestring import mark_safe

from registry import registration
from registry import models as registry_models

class SelectorKeyField(models.CharField):
  """
  A character field that supports choices derived from a pre-registered choice set.
  When the field is rendered inside the registry formset, any modifications to it
  will cause the forms to be recomputed.
  """
  def __init__(self, regpoint, enum_id, *args, **kwargs):
    """
    Class constructor.
    """
    kwargs['max_length'] = 50
    self._choices = kwargs['choices'] = registration.point(regpoint).get_registered_choices(enum_id)
    super(SelectorKeyField, self).__init__(*args, **kwargs)
  
  def formfield(self, **kwargs):
    """
    Returns an augmented form field.
    """
    defaults = { 'widget' : widgets.Select(attrs = { 'class' : 'regact_selector' }) }
    defaults.update(kwargs) 
    field = super(SelectorKeyField, self).formfield(**defaults)
    field._rp_choices = self._choices
    
    def modify_to_context(slf, item, cfg):
      def resolve_path(loc):
        path, attribute = loc.split('#')
        return reduce(getattr, attribute.split('.'), cfg[path][0])
      
      slf.choices = BLANK_CHOICE_DASH + slf._rp_choices.subset_choices(lambda path, value: resolve_path(path) == value)
    
    field.__class__.modify_to_context = modify_to_context
    return field

class ModelSelectorKeyField(models.ForeignKey):
  """
  A standard foreign key that augments the resulting form widget with a special
  selector class that will cause the forms to be recomputed when this field is
  modified.
  """
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    kwargs['on_delete'] = models.PROTECT
    super(ModelSelectorKeyField, self).__init__(*args, **kwargs)
  
  def formfield(self, **kwargs):
    """
    Returns an augmented form field.
    """
    defaults = { 'widget' : widgets.Select(attrs = { 'class' : 'regact_selector' }) }
    defaults.update(kwargs) 
    return super(ModelSelectorKeyField, self).formfield(**defaults)

class IntraRegistryRelatedObjectDescriptor(models.fields.related.ForeignRelatedObjectsDescriptor):
  """
  Descriptor for accessing related objects of a intra-registry foreign key that
  adds support for virtual relations in case of partially validated models.
  """
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    super(IntraRegistryRelatedObjectDescriptor, self).__init__(*args, **kwargs)
  
  def __get__(self, instance, instance_type = None):
    """
    Adds support for accessing virtual relations, since partially validated models
    can't be saved and therefore references don't work.
    """
    if not hasattr(instance, '_registry_virtual_model'):
      return super(IntraRegistryRelatedObjectDescriptor, self).__get__(instance, instance_type)
    elif instance is None:
      return self
    else:
      return getattr(instance, '_registry_virtual_relation', {}).get(self, [])
  
  def __set__(self, instance, value):
    """
    Adds support for setting virtual relations, since partially validated models
    can't be saved and therefore references don't work.
    """
    if not hasattr(instance, '_registry_virtual_model'):
      super(IntraRegistryRelatedObjectDescriptor, self).__set__(instance, value)
    else:
      instance._registry_virtual_relation[self] = value

class IntraRegistryForeignKey(models.ForeignKey):
  """
  A field for connecting registry items into a hierarchy.
  """
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    super(IntraRegistryForeignKey, self).__init__(*args, **kwargs)
  
  def contribute_to_related_class(self, cls, related):
    """
    Modifies the accessor descriptor so our own class is used instead of
    the standard one.
    """
    super(IntraRegistryForeignKey, self).contribute_to_related_class(cls, related)
    setattr(cls, related.get_accessor_name(), IntraRegistryRelatedObjectDescriptor(related))

