from django import forms
from django.db import transaction
from django.forms.formsets import formset_factory

from core import cgm
from core.cgm import base as cgm_base
from registry import state as registry_state
from registry import rules as registry_rules

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
      widget = forms.Select(attrs = { 'class' : 'regact_item_chooser' }) if len(items) > 1 else forms.HiddenInput
    )

class RegistrySetMetaForm(forms.Form):
  form_count = forms.IntegerField(
    min_value = 0,
    max_value = 10,
    widget = forms.HiddenInput
  )

def generate_forms_for_item_cls(node, mdl, cls_meta, data, items, save, prefix, idx = 0):
  """
  A helper function for generating forms.
  """
  selected_item = None
  item_forms = []
  validation_errors = False
  
  if save:
    meta_form = RegistryMetaForm(items, data = data, prefix = prefix)
    if not meta_form.is_valid():
      validation_errors = True
  
  for item_cls in items:
    # Attempt to retrieve the existing configuration for this node when set
    form_cls = item_cls.get_form()
    selected_form = False
    item_mdl = mdl
    
    if node is not None:
      if item_mdl is not None:
        if item_mdl.cls_id != item_cls._meta.module_name:
          # The model exists, but it is not the same as the one for which we are
          # generating a form so we must perform field copying to a new instance
          merge_mdl = item_cls(node = node)
          item_fields = set(item_mdl._meta.get_all_field_names())
          merge_fields = set(merge_mdl._meta.get_all_field_names())
          for field in item_fields.intersection(merge_fields):
            try:
              if getattr(item_mdl, field, None) is not None:
                setattr(merge_mdl, field, getattr(item_mdl, field))
            except ValueError:
              pass
          item_mdl = merge_mdl
        else:
          selected_form = True
          selected_item = item_cls._meta.module_name
      else:
        # This object doesn't have this item configured, so we simply use an
        # empty form for it
        item_mdl = item_cls(node = node)
    else:
      item_mdl = item_cls(node = node)
    
    form = form_cls(data, instance = item_mdl, prefix = prefix + '_' + item_cls._meta.module_name)
    if save and item_cls._meta.module_name == meta_form.cleaned_data['item']:
      if form.is_valid():
        form.save()
      else:
        validation_errors = True
    
    # Augment form fields with classes so they are easily locatable using the client-side API
    for name, field in form.fields.iteritems():
      widget_class = cls_meta.registry_id.replace('.', '_') + '_' + name + '_' + str(idx)
      field.widget.attrs['class'] = field.widget.attrs.get('class', '') + " regfld_" + widget_class
    
    form.selected = selected_form
    item_forms.append(form)
  
  # Ensure that at least one form is selected
  if not selected_item:
    item_forms[0].selected = True
    selected_item = items[0]._meta.module_name
  
  if not save:
    meta_form = RegistryMetaForm(items, selected_item, data = data, prefix = prefix)
  
  return validation_errors, item_forms, meta_form

def prepare_forms_for_node(node = None, data = None, save = False, only_rules = False):
  """
  Prepares a list of configuration forms for use on a node's
  configuration page.
  """
  try:
    sid = transaction.savepoint()
    validation_errors = False
    forms = []
    
    for _, items in registry_state.ITEM_LIST.iteritems():
      cls_meta = items[0].RegistryMeta
      base_prefix = "reg_" + cls_meta.registry_id.replace('.', '_')
      subforms = []
      
      mdl = node.config.by_path(cls_meta.registry_id)
      if getattr(cls_meta, 'multiple', False):
        if not save:
          # We are generating forms for display purpuses, only include forms for
          # existing models
          for idx, item_mdl in enumerate(node.config.by_path(cls_meta.registry_id)):
            has_errors, item_forms, meta_form = generate_forms_for_item_cls(
              node, item_mdl, cls_meta, data, items, save, base_prefix + '_mu_' + str(idx), idx
            )
            if has_errors:
              validation_errors = True
            
            subforms.append({
              'prefix'  : base_prefix + '_mu_' + str(idx),
              'meta'    : meta_form,
              'forms'   : item_forms
            })
          
          submeta = RegistrySetMetaForm(data, prefix = base_prefix + '_sm', initial = {
            'form_count' : len(subforms)
          })
        else:
          # We are saving so some forms might have been added and others might have been removed,
          # so we generate forms; delete all items as they will be added again
          node.config.by_path(cls_meta.registry_id, queryset = True).delete()
          submeta = RegistrySetMetaForm(data, prefix = base_prefix + '_sm')
          if not submeta.is_valid():
            validation_errors = True
          
          for idx in xrange(submeta.cleaned_data['form_count']):
            has_errors, item_forms, meta_form = generate_forms_for_item_cls(
              node, None, cls_meta, data, items, save, base_prefix + '_mu_' + str(idx), idx
            )
            if has_errors:
              validation_errors = True
            
            subforms.append({
              'prefix'  : base_prefix + '_mu_' + str(idx),
              'meta'    : meta_form,
              'forms'   : item_forms
            })
        
        # Generate an extra subform for new objects (this is never saved)
        _, item_forms, meta_form = generate_forms_for_item_cls(node, None, cls_meta, None, items, False, base_prefix + '_stub', 'stub')
        subforms.append({
          'prefix'  : base_prefix + '_stub',
          'meta'    : meta_form,
          'forms'   : item_forms,
          'stub'    : True
        })
      else:
        # Only a single item can be selected for this form
        mdl = node.config.by_path(cls_meta.registry_id)
        has_errors, item_forms, meta_form = generate_forms_for_item_cls(node, mdl, cls_meta, data, items, save, base_prefix)
        if not item_forms:
          continue
        if has_errors:
          validation_errors = True
        
        submeta = None
        subforms.append({
          'prefix'  : base_prefix,
          'meta'    : meta_form,
          'forms'   : item_forms
        })
      
      forms.append({
        'name'        : cls_meta.registry_section,
        'id'          : cls_meta.registry_id,
        'multiple'    : getattr(cls_meta, 'multiple', False),
        'subforms'    : subforms,
        'submeta'     : submeta,
        'prefix'      : base_prefix
      })
    
    if only_rules:
      # If only rule validation is requested, we should evaluate rules and then rollback
      # the savepoint in any case; all validation errors are ignored
      actions = registry_rules.evaluate(node)
      transaction.savepoint_rollback(sid)
      return actions
    
    if save and node and not validation_errors:
      # When save is enabled, we must perform node configuration validation
      try:
        cgm.generate_config(node, only_validate = True)
      except cgm_base.ValidationError, e:
        validation_errors = True
        # TODO Handle validation errors
        raise
    
    if not validation_errors:
      transaction.savepoint_commit(sid)
    else:
      transaction.savepoint_rollback(sid)
  except cgm_base.ValidationError:
    transaction.savepoint_rollback(sid)
  except:
    transaction.savepoint_rollback(sid)
    raise
  
  return forms if not save else (validation_errors, forms)

