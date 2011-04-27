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
  
  @classmethod
  def lookup_path(cls):
    """
    Returns a query filter "path" that can be used for performing node lookups with
    fields that are part of some registry object.
    """
    if cls.__base__ == RegistryItem:
      return 'config_' + cls._meta.app_label + '_' + cls._meta.module_name
    else:
      return lookup_path(cls.__base__) + '__' + cls._meta.module_name
  
  @classmethod
  def top_model(cls):
    """
    Returns the top-level model for this registry item.
    """
    if cls.__base__ == RegistryItem:
      return cls
    else:
      return cls.__base__.top_model()
  
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
  
  # Sanity check for object names
  if '_' in sender._meta.object_name:
    raise ImproperlyConfigured("Registry items must not have underscores in class names!")
  
  items = registry_state.ITEM_LIST 
  item_dict = items.setdefault((sender.RegistryMeta.form_order, sender.RegistryMeta.registry_id), {})
  item_dict[sender._meta.module_name] = sender
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
  
  # Register proxy fields for node lookup
  lookup_proxies = getattr(sender.RegistryMeta, 'lookup_proxies', None)
  if lookup_proxies is not None:
    for field in lookup_proxies:
      if isinstance(field, (tuple, list)):
        src_field, dst_fields = field
      else:
        src_field = dst_fields = field
      
      if not isinstance(dst_fields, (tuple, list)):
        dst_fields = (dst_fields,)
      
      for dst_field in dst_fields:
        # Ignore registrations of existing proxies
        if dst_field in registry_state.FLAT_LOOKUP_PROXIES:
          continue
        
        registry_state.FLAT_LOOKUP_PROXIES[dst_field] = sender, src_field

model_signals.class_prepared.connect(prepare_config_item)

