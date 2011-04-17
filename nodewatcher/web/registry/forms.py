from registry import state as registry_state

def prepare_forms_for_node(node = None):
  """
  Prepares a list of configuration forms for use on a node's
  configuration page.
  """
  forms = []
  for _, items in registry_state.ITEM_LIST.iteritems():
    meta = None
    has_selected = False
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
            has_selected = True
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
    if not has_selected:
      item_forms[0].selected = True
    
    # TODO meta form should include a form with a combo selector for potential
    #      subclasses if there is more than one
    
    forms.append({
      'name' : item_cls.RegistryMeta.registry_name,
      'meta' : meta,
      'forms' : item_forms
    })
  
  return forms

