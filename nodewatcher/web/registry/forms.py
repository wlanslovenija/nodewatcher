import copy
import json

from django import forms, template
from django.core import exceptions
from django.db import transaction

from web.registry import rules as registry_rules
from web.registry import registration
from web.registry.cgm import base as cgm_base

class RegistryValidationError(Exception):
  """
  This exception can be raised by registry point validation hooks to
  notify the API that validation has failed.
  """
  pass

class RegistryFormAction(object):
  """
  An abstract action that can modify lists of registry forms.
  """
  def modify_forms_before(self):
    """
    Subclasses should provide action implementation in this method. It
    will be executed before the subforms are generated.
    """
    pass
  
  def modify_forms_after(self):
    """
    Subclasses should provide action implementation in this method. It
    will be executed after the subforms are generated.
    """
    pass

class ClearFormsAction(RegistryFormAction):
  """
  An action that clears all subforms for the specified registry class.
  """
  def modify_forms_after(self):
    """
    Clears all subforms.
    """
    self.context.subforms = []
    return True

class RemoveLastFormAction(RegistryFormAction):
  """
  An action that removes the last subform.
  """
  def modify_forms_after(self):
    """
    Removes the last subform.
    """
    if len(self.context.subforms) > 0:
      self.context.subforms.pop()
      return True

class AppendFormAction(RegistryFormAction):
  """
  An action that appends a new form at the end of current subforms.
  """
  def __init__(self, item_cls, attributes):
    """
    Class constructor.
    
    @param item_cls: Item class
    @param attributes: A dictionary of initial values
    """
    self.item_cls = item_cls
    self.attributes = attributes
  
  def modify_forms_after(self):
    """
    Appends a new form at the end of current subforms.
    """
    form_prefix = self.context.base_prefix + '_mu_' + str(len(self.context.subforms))
    mdl = self.item_cls if self.item_cls is not None else self.context.default_item_cls
    mdl = mdl(root = self.context.root, **self.attributes)
    
    self.context.subforms.append(generate_form_for_class(
      self.context,
      form_prefix,
      None,
      len(self.context.subforms),
      instance = mdl,
      validate = True,
      force_selector_widget = self.context.force_selector_widget
    ))
    
    return True

class AssignToFormAction(RegistryFormAction):
  """
  An action that assigns to an existing form.
  """
  def __init__(self, index, attributes):
    """
    Class constructor.
    
    @param index: Subform index
    @param attributes: A dictionary of assigned
    """
    self.index = index
    self.attributes = attributes
  
  def modify_forms_before(self):
    """
    Assigns to an existing form.
    """
    # TODO
    pass

class BasicRegistryRenderItem(object):
  """
  A simple registry render item that includes a form with fields and
  an item class selector when needed.
  """
  template = 'registry/basic_render_item.html'
  
  def __init__(self, form, meta_form, **kwargs):
    """
    Class constructor.
    
    @param form: Form containing the fields
    @param meta_form: Form containing selected item metadata
    """
    self.form = form
    self.meta_form = meta_form
    self.args = kwargs
  
  @property
  def media(self):
    """
    Returns the form Media object for this render item.
    """
    if self.form is not None and self.meta_form is not None:
      return self.form.media + self.meta_form.media
    else:
      return None
  
  def __unicode__(self):
    """
    Renders this item.
    """
    t = template.loader.get_template(self.template)
    args = {
      'form' : self.form,
      'meta' : self.meta_form
    }
    args.update(self.args)
    return t.render(template.Context(args))

class NestedRegistryRenderItem(BasicRegistryRenderItem):
  """
  A registry renderer item that augments the basic form with support for
  nested forms.
  """
  template = 'registry/nested_render_item.html'
  
  def __init__(self, form, meta_form, children):
    """
    Class constructor.
    
    @param form: Form containing the fields
    @param meta_form: Form containing selected item metadata
    @param children: A list of child form descriptors
    """
    super(NestedRegistryRenderItem, self).__init__(form, meta_form, registry_forms = children)
    self.children = children
  
  @property
  def media(self):
    """
    Returns the form Media object for this render item.
    """
    base_media = super(NestedRegistryRenderItem, self).media
    
    for child in self.children:
      # Include media from all child render items
      for subform in child['subforms']:
        if base_media is not None:
          base_media += subform.media
        else:
          base_media = subform.media
      
      # Include media from meta form
      if child['submeta'] is not None:
        base_media += child['submeta'].media
    
    return base_media

class RootRegistryRenderItem(NestedRegistryRenderItem):
  """
  A registry render item that is returned as the root of the render
  tree. It contains and renders all top-level forms.
  """
  template = 'registry/render_items.html'
  
  def __init__(self, forms):
    """
    Class constructor.
    
    @param forms: A list of form descriptors
    """
    super(RootRegistryRenderItem, self).__init__(None, None, forms)
  
  def __unicode__(self):
    """
    Renders this item.
    """
    t = template.loader.get_template(self.template)
    args = { 'registry_forms' : self.children }
    return t.render(template.Context(args))

class RegistryMetaForm(forms.Form):
  def __init__(self, items, selected_item = None, force_selector_widget = False, static = False, *args, **kwargs):
    """
    Class constructor.
    """
    super(RegistryMetaForm, self).__init__(*args, **kwargs)
    
    if selected_item is None:
      selected_item = items.values()[0]
    selected_item = selected_item._meta.module_name
    
    if not static and (len(items) > 1 or force_selector_widget):
      item_widget = forms.Select(attrs = { 'class' : 'regact_item_chooser' })
    else:
      item_widget = forms.HiddenInput
    
    self.fields['item'] = forms.TypedChoiceField(
      choices = [(name, item.RegistryMeta.registry_name) for name, item in items.iteritems()],
      coerce = str,
      initial = selected_item,
      widget = item_widget
    )
    self.fields['prev_item'] = forms.TypedChoiceField(
      choices = [(name, item.RegistryMeta.registry_name) for name, item in items.iteritems()],
      coerce = str,
      initial = selected_item,
      widget = forms.HiddenInput
    )

class RegistrySetMetaForm(forms.Form):
  form_count = forms.IntegerField(
    min_value = 0,
    max_value = 10,
    widget = forms.HiddenInput
  )

def generate_form_for_class(context, prefix, data, index, instance = None, validate = False, partial = None,
                            force_selector_widget = False, static = False):
  """
  A helper function for generating a form for a specific registry item class.
  """
  selected_item = instance.__class__ if instance is not None else None
  previous_item = None
  
  # Parse a form that holds the item selector
  meta_form = RegistryMetaForm(context.items, selected_item, data = data, prefix = prefix,
    force_selector_widget = force_selector_widget,
    static = static
  )
  if validate and not static:
    if not meta_form.is_valid():
      context.validation_errors = True
    else:
      selected_item = context.items.get(meta_form.cleaned_data['item'])
      previous_item = context.items.get(meta_form.cleaned_data['prev_item'])
  
  # Fallback to default item in case of severe problems (this should not happen in normal
  # operation, but might happen when someone tampers with the form)
  if selected_item is None:
    selected_item = context.items.values()[0]
  
  # Items have changed between submissions, we should copy some field values from the
  # previous form to the new one
  if previous_item is not None and selected_item != previous_item and not static:
    pform = previous_item.get_form()(
      data,
      prefix = prefix + '_' + previous_item._meta.module_name
    )
    
    # Perform a partial clean and copy all valid fields to the new form
    pform.cleaned_data = {}
    pform._errors = {}
    pform._clean_fields()
    initial = {}
    for field in pform.cleaned_data.keys():
      data[prefix + '_' + selected_item._meta.module_name + '-' + field] = \
        data[prefix + '_' + previous_item._meta.module_name + '-' + field]
  
  # When there is no instance, we should create one so we will be able to save somewhere
  if validate and partial is None and instance is None:
    instance = selected_item(root = context.root)
    if context.hierarchy_parent_cls is not None:
      setattr(
        instance,
        selected_item._registry_parents[context.hierarchy_parent_cls].name,
        context.hierarchy_parent_obj
      )
  
  # Now generate a form for the selected item
  form_prefix = prefix + '_' + selected_item._meta.module_name
  form = selected_item.get_form()(
    data,
    instance = instance,
    prefix = form_prefix
  )
  
  # Discover the current item model in the partially validated config hierarchy
  current_config_item = None
  if context.current_config is not None:
    try:
      if context.hierarchy_parent_current is not None:
        current_config_item = getattr(
          context.hierarchy_parent_current,
          selected_item._registry_parents[context.hierarchy_parent_cls].rel.related_name
        )[index]
      else:
        current_config_item = context.current_config[selected_item.RegistryMeta.registry_id][index]
    except (IndexError, KeyError):
      current_config_item = None
  else:
    current_config_item = None
  
  def modify_to_context(obj):
    if not hasattr(obj, 'modify_to_context'):
      return
    
    item = current_config_item or instance
    cfg = context.current_config or context.regpoint.get_accessor(context.root).to_partial()
    obj.modify_to_context(item, cfg)
  
  if partial is None:
    # Enable forms to modify themselves accoording to current context
    modify_to_context(form)
  
    # Enable form fields to modify themselves accoording to current context
    for name, field in form.fields.iteritems():
      modify_to_context(field)
  
  config = None
  if validate:
    if partial is None:
      # Perform a full validation and save the form
      if form.is_valid():
        # Avoid an integrity error when the parent model has failed validation and had not
        # been saved; when this happens the parent does not have an id and saving a child will fail
        if context.hierarchy_parent_obj is not None and not context.hierarchy_parent_obj.pk:
          context.validation_errors = True
        else:
          form.save()
      else:
        context.validation_errors = True
    else:
      # We are only interested in all the current values even if they might be incomplete
      # and/or invalid, so we can't do full form validation
      form.cleaned_data = {}
      form._errors = {}
      form._clean_fields()
      config = selected_item()
      config._registry_virtual_model = True
      if context.hierarchy_parent_partial is not None:
        setattr(
          config,
          selected_item._registry_parents[context.hierarchy_parent_cls].name,
          context.hierarchy_parent_partial
        )
        
        # Create a virtual reverse relation in the parent object
        virtual_relation = getattr(context.hierarchy_parent_partial, '_registry_virtual_relation', {})
        desc = getattr(
          context.hierarchy_parent_partial.__class__,
          selected_item._registry_parents[context.hierarchy_parent_cls].rel.related_name
        )
        virtual_relation.setdefault(desc, []).append(config)
        context.hierarchy_parent_partial._registry_virtual_relation = virtual_relation
      
      partial.setdefault(selected_item.RegistryMeta.registry_id, []).append(config)
      
      for field, value in form.cleaned_data.iteritems():
        setattr(config, field, value)
  
  # Generate a new meta form, since the previous item has now changed
  meta_form = RegistryMetaForm(context.items, selected_item, prefix = prefix,
    force_selector_widget = force_selector_widget,
    static = static
  )
  
  # Pack forms into a proper abstract representation
  if hasattr(selected_item, '_registry_has_children'):
    sub_context = RegistryFormContext(
      regpoint = context.regpoint,
      root = context.root,
      data = context.data,
      save = context.save,
      only_rules = context.only_rules,
      also_rules = context.also_rules,
      actions = context.actions,
      current_config = context.current_config,
      partial_config = context.partial_config,
      hierarchy_prefix = form_prefix,
      hierarchy_parent_cls = selected_item,
      hierarchy_parent_obj = instance,
      hierarchy_parent_partial = config,
      hierarchy_parent_current = current_config_item,
      validation_errors = False
    )
    
    forms = NestedRegistryRenderItem(form, meta_form, prepare_forms(sub_context))
    
    # Validation errors flag must propagate upwards
    if sub_context.validation_errors:
      context.validation_errors = True
  else:
    forms = BasicRegistryRenderItem(form, meta_form)
  
  return forms

class RegistryFormContext(object):
  """
  Form render context.
  """
  regpoint = None
  root = None
  data = None
  save = False
  only_rules = False
  also_rules = False
  actions = None
  currenct_config = None
  partial_config = None
  validation_errors = False
  subforms = None
  hierarchy_parent_cls = None
  hierarchy_parent_obj = None
  hierarchy_parent_partial = None
  hierarchy_parent_current = None
  hierarchy_prefix = None
  base_prefix = None
  default_item_cls = None
  force_selector_widget = False
  items = None
  item_actions = None
  
  def __init__(self, **kwargs):
    """
    Class constructor.
    """
    self.__dict__.update(kwargs)

def prepare_forms(context):
  """
  Prepares forms for some registry items.
  """
  forms = []
  for _, items in context.regpoint.item_list.iteritems():
    context.items = copy.deepcopy(items)
    item_cls = context.items.values()[0].top_model()
    cls_meta = item_cls.RegistryMeta
    
    # Skip items that are not child items
    if context.hierarchy_parent_cls not in getattr(item_cls, '_registry_parents', [None]):
      continue

    if context.hierarchy_prefix is not None:
      context.base_prefix = context.hierarchy_prefix + '_' + cls_meta.registry_id.replace('.', '_')
    else:
      context.base_prefix = "reg_" + cls_meta.registry_id.replace('.', '_')
    
    context.subforms = []
    context.force_selector_widget = False
    
    if getattr(cls_meta, 'hidden', False):
      # The top-level item should be hidden
      del context.items[item_cls._meta.module_name]
      context.force_selector_widget = True
      
      # When there is only the top-level item and it should be hidden, we don't
      # render this whole item class section
      if not context.items:
        continue
    
    # Remove all items that should not be visible
    for key, value in context.items.items():
      if value._registry_hide_requests > 0:
        del context.items[key]
      
      if context.hierarchy_parent_cls is not None:
        if value not in context.hierarchy_parent_cls._registry_allowed_children:
          del context.items[key]
    
    if not context.items:
      continue
    
    context.default_item_cls = context.items.values()[0]
    
    def existing_models_for_multiple():
      existing_models = []
      if context.root is not None:
        if context.hierarchy_parent_cls is not None:
          existing_models = context.regpoint.get_accessor(context.root).by_path(cls_meta.registry_id, queryset = True)
          existing_models = existing_models.filter(
            **{ item_cls._registry_parents[context.hierarchy_parent_cls].name : context.hierarchy_parent_obj }
          )
        else:
          existing_models = context.regpoint.get_accessor(context.root).by_path(cls_meta.registry_id)
      else:
        existing_models = []
      
      return existing_models
    
    if getattr(cls_meta, 'multiple', False):
      # This is an item class that supports multiple objects of the same class
      if getattr(cls_meta, 'multiple_static', False):
        # All multiple objects that are registered should always be displayed
        existing_models = existing_models_for_multiple()
        for index, item in enumerate(context.items.values()):
          mdl = None
          for emdl in existing_models:
            if isinstance(emdl, item):
              mdl = emdl
              break
          else:
            mdl = item(root = context.root)
          
          form_prefix = context.base_prefix + '_mu_' + str(index)
          context.subforms.append(generate_form_for_class(
            context,
            form_prefix,
            context.data,
            index,
            instance = mdl,
            validate = context.save or context.only_rules,
            partial = context.partial_config,
            static = True
          ))
      else:
        # Dynamically modifiable multiple objects
        if not context.save and not context.only_rules:
          # We are generating forms for first-time display purpuses, only include forms for
          # existing models
          existing_models = existing_models_for_multiple()
          
          for index, mdl in enumerate(existing_models):
            form_prefix = context.base_prefix + '_mu_' + str(index)
            context.subforms.append(generate_form_for_class(
              context,
              form_prefix,
              None,
              index,
              instance = mdl.cast(),
              force_selector_widget = context.force_selector_widget
            ))
          
          # Create the form that contains metadata for this formset
          submeta = RegistrySetMetaForm(
            context.data,
            prefix = context.base_prefix + '_sm',
            initial = { 'form_count' : len(context.subforms) }
          )
        else:
          # We are saving or preparing to evaluate rules, so we regenerate all items
          if context.hierarchy_parent_cls is not None:
            qs = context.regpoint.get_accessor(context.root).by_path(cls_meta.registry_id, queryset = True)
            qs = qs.filter(
              **{ item_cls._registry_parents[context.hierarchy_parent_cls].name : context.hierarchy_parent_obj }
            )
            qs.delete()
          else:
            context.regpoint.get_accessor(context.root).by_path(cls_meta.registry_id, queryset = True).delete()
          
          submeta = RegistrySetMetaForm(
            context.data,
            prefix = context.base_prefix + '_sm'
          )
          form_count = 0
          if submeta.is_valid():
            form_count = submeta.cleaned_data['form_count']
          else:
            submeta = RegistrySetMetaForm(
              prefix = context.base_prefix + '_sm',
              initial = { 'form_count' : 0 }
            )
          
          # TODO implement 'assign' action (its order is not relevant)
          context.item_actions = context.actions.get(context.base_prefix, []) + context.actions.get(cls_meta.registry_id, [])
          meta_modified = False
          
          # Generate the right amount of forms
          for index in xrange(form_count):
            form_prefix = context.base_prefix + '_mu_' + str(index)
            context.subforms.append(generate_form_for_class(
              context,
              form_prefix,
              context.data,
              index,
              validate = True,
              partial = context.partial_config,
              force_selector_widget = context.force_selector_widget
            ))
          
          # Check for any actions and execute them
          for action in context.item_actions:
            action.context = context
            if action.modify_forms_after():
              meta_modified = True
          
          if meta_modified:
            # If a form has been modified we cannot simply save, so we fake a validation
            # error so the user will be displayed the updated forms
            context.validation_errors = True
            
            # Update the submeta form with new count
            submeta = RegistrySetMetaForm(
              prefix = context.base_prefix + '_sm',
              initial = { 'form_count' : len(context.subforms) }
            )
    else:
      # This item class only supports a single object to be selected
      if context.root is not None:
        qs = context.regpoint.get_accessor(context.root).by_path(cls_meta.registry_id, queryset = True)
        if context.hierarchy_parent_cls is not None:
          qs = qs.filter(
            **{ item_cls._registry_parents[context.hierarchy_parent_cls].name : context.hierarchy_parent_obj }
          )
        
        if not context.save and not context.only_rules:
          try:
            mdl = qs.all()[0].cast()
          except IndexError:
            mdl = None
        else:
          qs.delete()
          mdl = None
      else:
        mdl = None
      
      form_prefix = context.base_prefix + '_mu_0'
      context.subforms.append(generate_form_for_class(
        context,
        form_prefix,
        context.data,
        0,
        instance = mdl,
        validate = context.save or context.only_rules,
        partial = context.partial_config
      ))
      
      submeta = None
    
    forms.append({
      'name'                    : cls_meta.registry_section,
      'id'                      : cls_meta.registry_id,
      'multiple'                : getattr(cls_meta, 'multiple', False),
      'hide_multiple_controls'  : getattr(cls_meta, 'multiple_static', False),
      'subforms'                : context.subforms,
      'submeta'                 : submeta,
      'prefix'                  : context.base_prefix
    })
  
  return forms

def prepare_forms_for_regpoint_root(regpoint, root = None, data = None, save = False, only_rules = False, also_rules = False, actions = None,
                                    current_config = None):
  """
  Prepares a list of configuration forms for use on a regpoint root's
  configuration page.
  
  @param regpoint: Registration point name or instance
  @param root: Registration point root instance for which to generate forms
  @param data: User-supplied POST data
  @param save: Are we performing a save or rendering an initial form
  @param only_rules: Should only rules be evaluated and a partial config generated
  @param also_rules: Should rules be evaluated (use only for initial state)
  @param actions: A list of actions that can modify forms
  @param current_config: An existing partial config dictionary
  """
  if save and only_rules:
    raise ValueError("You cannot use save and only_rules at the same time!")
  
  if isinstance(regpoint, basestring):
    regpoint = registration.point(regpoint)
  
  # Transform data into a mutable dictionary in case an immutable one is passed
  data = copy.copy(data)
  actions = actions if actions is not None else {}
  
  # Prepare context
  context = RegistryFormContext(
    regpoint = regpoint,
    root = root,
    data = data,
    save = save,
    only_rules = only_rules,
    also_rules = also_rules,
    actions = actions,
    current_config = current_config,
    partial_config = {} if only_rules else None,
    validation_errors = False
  )
  
  try:
    sid = transaction.savepoint()
    forms = RootRegistryRenderItem(prepare_forms(context))
    
    if only_rules:
      # If only rule validation is requested, we should evaluate rules and then rollback
      # the savepoint in any case; all validation errors are ignored
      actions = registry_rules.evaluate(regpoint, root, json.loads(data['STATE']), context.partial_config)
      transaction.savepoint_rollback(sid)
      return actions, context.partial_config
    elif also_rules:
      actions = registry_rules.evaluate(regpoint, root, {}, {})
    
    # Execute any validation hooks when saving and there are no validation errors
    if save and root is not None and not context.validation_errors:
      for hook in regpoint.validation_hooks.values():
        try:
          hook(root)
        except RegistryValidationError, e:
          context.validation_errors = True
          # TODO Handle validation errors
          raise
    
    if not context.validation_errors:
      transaction.savepoint_commit(sid)
    else:
      transaction.savepoint_rollback(sid)
  except RegistryValidationError:
    transaction.savepoint_rollback(sid)
  except:
    transaction.savepoint_rollback(sid)
    raise
  
  # Also return (initial) evaluation state when requested
  if also_rules:
    return forms, actions["STATE"]
  
  return forms if not save else (context.validation_errors, forms)

