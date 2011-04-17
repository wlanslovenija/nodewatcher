from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import signals as model_signals

from registry import state as registry_state

class RegistryItem(models.Model):
  """
  An abstract registry configuration item.
  """
  node = models.ForeignKey('nodes.Node', null = True, editable = False, related_name = 'config_%(app_label)s_%(class)s')
  cls_id = models.CharField(max_length = 200, editable = False)
  
  class Meta:
    abstract = True
  
  @classmethod
  def get_form(cls):
    """
    Returns the form used for this model.
    """
    if hasattr(cls, '_forms'):
      form = cls._forms.get(cls)
    
    if form is None:
      class DefaultRegistryItemForm(forms.ModelForm):
        class Meta:
          model = cls
      
      form = DefaultRegistryItemForm
    
    return form
  
  def save(self, *args, **kwargs):
    """
    Sets up and saves the configuration item.
    """
    self.cls_id = self._meta.module_name
    super(RegistryItem, self).save(*args, **kwargs)

def prepare_config_item(sender, **kwargs):
  """
  Prepares the configuration item model by registering it in the config
  store.
  """
  if not issubclass(sender, RegistryItem):
    return
  
  registry_state.ITEM_LIST.append(sender)
  registry_state.ITEM_LIST.sort(key = lambda x: (x.RegistryMeta.form_order, x.RegistryMeta.registry_name))
  
  # Only record the top-level item in the registry as there could be multiple
  # specializations that define their own limits
  if sender.__base__ == RegistryItem:
    registry_id = sender.RegistryMeta.registry_id
    if registry_id in registry_state.ITEM_REGISTRY:
      raise ImproperlyConfigured(
        "Multiple top-level registry items claim identifier '{0}'! Claimed by '{1}' and '{2}'.".format(
          registry_id, registry_state.ITEM_REGISTRY[registry_id]._meta.object_name, sender._meta.object_name
      ))
    
    registry_state.ITEM_REGISTRY[registry_id] = sender

model_signals.class_prepared.connect(prepare_config_item)

