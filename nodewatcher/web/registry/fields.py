import types

from django.core import exceptions
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import widgets
from django.utils.safestring import mark_safe

from registry import registration
from registry import models as registry_models

class SelectorKeyField(models.CharField):
  def __init__(self, regpoint, enum_id, *args, **kwargs):
    """
    Class constructor.
    """
    kwargs['max_length'] = 50
    self._choices = kwargs['choices'] = registration.point(regpoint).get_registered_choices(enum_id)
    super(SelectorKeyField, self).__init__(*args, **kwargs)
  
  def formfield(self, **kwargs):
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
  def __init__(self, *args, **kwargs):
    """
    Class constructor.
    """
    kwargs['on_delete'] = models.PROTECT
    super(ModelSelectorKeyField, self).__init__(*args, **kwargs)
  
  def formfield(self, **kwargs):
    defaults = { 'widget' : widgets.Select(attrs = { 'class' : 'regact_selector' }) }
    defaults.update(kwargs) 
    return super(ModelSelectorKeyField, self).formfield(**defaults)

