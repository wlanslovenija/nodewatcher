from django import forms
from django.db import transaction

from core import cgm
from core.cgm import base as cgm_base
from registry import state as registry_state

class RegistryMetaForm(forms.Form):
  def __init__(self, items, selected_item = None, *args, **kwargs):
    """
    Class constructor.
    """
    super(RegistryMetaForm, self).__init__(*args, **kwargs)
    
    self.fields['item'] = forms.TypedChoiceField(
      choices = [(item._meta.module_name, item.RegistryMeta.registry_name) for item in items],
      coerce = str,
      initial = selected_item,
      widget = forms.Select(attrs = { 'class' : 'config_selector' }) if len(items) > 1 else forms.HiddenInput
    )

def prepare_forms_for_node(node = None, data = None, save = False):
  """
  Prepares a list of configuration forms for use on a node's
  configuration page.
  """
  try:
    sid = transaction.savepoint()
    validation_errors = False
    forms = []
    
    for _, items in registry_state.ITEM_LIST.iteritems():
      selected_item = None
      item_forms = []
      
      # XXX just until we have multiples implemented
      if getattr(items[0].RegistryMeta, 'multiple', False):
        continue
      
      if save:
        meta_form = RegistryMetaForm(items, data = data, prefix = items[0].RegistryMeta.registry_id.replace('.', '_'))
        if not meta_form.is_valid():
          validation_errors = True
          break
      
      for item_cls in items:
        # Attempt to retrieve the existing configuration for this node when set
        form_cls = item_cls.get_form()
        selected_form = False
        
        if not getattr(item_cls.RegistryMeta, 'multiple', False):
          # Single configuration option
          if node is not None:
            try:
              mdl = node.config.by_path(item_cls.RegistryMeta.registry_id)
              
              if mdl.cls_id != item_cls._meta.module_name:
                # The model exist, but it is not the same as the one for which we are
                # generating a form so we must perform field copying to a new instance
                merge_mdl = item_cls(node = node)
                for field in mdl._meta.get_all_field_names():
                  if hasattr(merge_mdl, field):
                    setattr(merge_mdl, field, getattr(mdl, field))
                mdl = merge_mdl
              else:
                selected_form = True
                selected_item = item_cls._meta.module_name
            except item_cls.DoesNotExist:
              # This object doesn't have this item configured, so we simply use an
              # empty form for it
              mdl = item_cls(node = node)
          else:
            mdl = item_cls(node = node)
          
          form = form_cls(data, instance = mdl, prefix = item_cls._meta.module_name)
          if save and item_cls._meta.module_name == meta_form.cleaned_data['item']:
            if form.is_valid():
              form.save()
            else:
              validation_errors = True
        else:
          # Multiple possible configuration instances
          # TODO
          continue
        
        form.selected = selected_form
        item_forms.append(form)
      
      if not item_forms:
        continue
      
      # Ensure that at least one form is selected
      if not selected_item:
        item_forms[0].selected = True
        selected_item = items[0]._meta.module_name
      
      if not save:
        meta_form = RegistryMetaForm(items, selected_item, data = data, prefix = items[0].RegistryMeta.registry_id.replace('.', '_'))
      
      forms.append({
        'name' : items[0].RegistryMeta.registry_section,
        'meta' : meta_form,
        'forms' : item_forms,
        'registry_id' : items[0].RegistryMeta.registry_id.replace('.', '_')
      })
    
    if save and node and not validation_errors:
      # When save is enabled, we must perform node configuration validation
      try:
        cgm.generate_config(node, only_validate = True)
      except cgm_base.ValidationError, e:
        validation_errors = True
        # TODO Handle validation errors
        raise
    
    transaction.savepoint_commit(sid)
  except cgm_base.ValidationError:
    transaction.savepoint_rollback(sid)
  except:
    transaction.savepoint_rollback(sid)
    raise
  
  return forms if not save else (validation_errors, forms)

