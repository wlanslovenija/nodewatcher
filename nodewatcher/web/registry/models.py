from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import models
from django.db.models import signals as model_signals
from django.utils import datastructures

from registry import state as registry_state

class RegistryItem(models.Model):
  """
  An abstract registry configuration item.
  """
  node = models.ForeignKey('nodes.Node', null = True, editable = False, related_name = 'config_%(app_label)s_%(class)s')
  content_type = models.ForeignKey(ContentType, editable = False)
  
  class Meta:
    abstract = True
    ordering = ['id']
  
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
  
  def cast(self):
    """
    Casts this registry item into the proper downwards type.
    """
    mdl = self.content_type.model_class()
    if mdl == self.__class__:
      return self
    
    return mdl.objects.get(pk = self.pk)
  
  def save(self, *args, **kwargs):
    """
    Sets up and saves the configuration item.
    """
    # Set class identifier
    self.content_type = ContentType.objects.get_for_model(self.__class__)
    super(RegistryItem, self).save(*args, **kwargs)
    
    # If only one configuration instance should be allowed, we
    # should delete existing ones
    if not getattr(self.RegistryMeta, 'multiple', False) and self.node:
      top_level = registry_state.ITEM_REGISTRY[self.RegistryMeta.registry_id]
      cfg = getattr(self.node, "config_{0}_{1}".format(top_level._meta.app_label, top_level._meta.module_name))
      cfg.exclude(pk = self.pk).delete()

def prepare_config_item(sender, **kwargs):
  """
  Prepares the configuration item model by registering it in the config
  store.
  """
  if not issubclass(sender, RegistryItem):
    return
  
  items = registry_state.ITEM_LIST 
  items.setdefault((sender.RegistryMeta.form_order, sender.RegistryMeta.registry_id), []).append(sender)
  registry_state.ITEM_LIST = datastructures.SortedDict(sorted(items.items(), key = lambda x: x[0]))
  
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

