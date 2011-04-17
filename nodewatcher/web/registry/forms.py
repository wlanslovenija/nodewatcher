from django import forms

from registry import state as registry_state

class RegistryMetaForm(forms.Form):
  def __init__(self, items, selected_item, *args, **kwargs):
    """
    Class constructor.
    """
    super(RegistryMetaForm, self).__init__(*args, **kwargs)
    
    self.fields['item'] = forms.TypedChoiceField(
      choices = [(item._meta.module_name, item.RegistryMeta.registry_name) for item in items],
      coerce = str,
      initial = selected_item,
      widget = forms.Select if len(items) > 1 else forms.HiddenInput
    )

def prepare_forms_for_node(node = None):
  """
  Prepares a list of configuration forms for use on a node's
  configuration page.
  """
  forms = []
  for _, items in registry_state.ITEM_LIST.iteritems():
    selected_item = None
    item_forms = []
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
              # The model exist, but it is not the same as this for which we are
              # generating a form, so we must perform field copying to a fake
              # instance that will never be saved
              merge_mdl = item_cls()
              for field in mdl._meta.get_all_field_names():
                if hasattr(merge_mdl, field):
                  setattr(merge_mdl, field, getattr(mdl, field))
              mdl = merge_mdl
            
            form = form_cls(instance = mdl, prefix = item_cls._meta.module_name)
            selected_form = True
            selected_item = item_cls._meta.module_name
          except form_cls.DoesNotExist:
            # This object doesn't have this item configured, so we simply use an
            # empty form for it
            form = form_cls(prefix = item_cls._meta.module_name)
        else:
          form = form_cls(prefix = item_cls._meta.module_name)
      else:
        # Multiple possible configuration instances
        # TODO
        continue
      
      form.selected = selected_form
      item_forms.append(form)
    
    if not item_forms:
      continue
    
    # Ensure that at least one form is selected (the default one)
    if not selected_item:
      item_forms[0].selected = True
      selected_item = items[0]._meta.module_name
    
    forms.append({
      'name' : items[0].RegistryMeta.registry_name,
      'meta' : RegistryMetaForm(items, selected_item, prefix = items[0].RegistryMeta.registry_id),
      'forms' : item_forms
    })
  
  return forms

def save_forms_for_node(node = None):
  pass

