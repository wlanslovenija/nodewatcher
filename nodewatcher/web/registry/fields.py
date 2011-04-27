from django.core import exceptions
from django.db import models
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
    kwargs['choices'] = registration.point(regpoint).get_registered_choices(enum_id)
    super(SelectorKeyField, self).__init__(*args, **kwargs)
  
  def formfield(self, **kwargs):
    defaults = { 'widget' : widgets.Select(attrs = { 'class' : 'regact_selector' }) }
    defaults.update(kwargs) 
    return super(SelectorKeyField, self).formfield(**defaults)

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

