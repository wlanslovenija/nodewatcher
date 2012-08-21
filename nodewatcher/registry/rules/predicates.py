import hashlib
import inspect

from nodewatcher.registry import access as registry_access
from nodewatcher.registry import forms as registry_forms
from nodewatcher.registry.rules.engine import *
from nodewatcher.registry.cgm import base as cgm_base 

# Exports
__all__ = [
  'rule',
  'value',
  'router_descriptor',
  'count',
  'foreach',
  'loop_var',
  'contains',
  'changed',
  'assign',
  'remove',
  'append',
]

def rule(condition, *args):
  """
  The rule predicate is used to define rules.
  
  @param condition: Lazy expression that represents a condition
  """
  if not isinstance(condition, (LazyValue, RuleModifier)):
    raise CompilationError("Rule conditions must be lazy values or rule modifiers!")
  
  ctx = inspect.stack()[1][0].f_locals.get('ctx')
  if not isinstance(ctx, EngineContext):
    raise CompilationError("Expecting engine context as 'ctx' variable in parent local scope!")
  
  for x in args:
    if not isinstance(x, (Action, Rule)):
      raise CompilationError("Rule actions must be Action or Rule instances!")
    
    # Since the rule predicate calls can be nested we must ensure that only top-level
    # rules remain in the context list; this is especially a problem since rule predicates
    # are first executed in sublevels by the Python interpreter
    if isinstance(x, Rule):
      ctx._rules.remove(x)
  
  new_rule = Rule(condition, args)
  ctx._rules.append(new_rule)
  return new_rule

def assign(location, index = 0, **kwargs):
  """
  Action that assigns a dictionary of values to a specific location.
  
  @param location: Registry location
  @param index: Optional array index
  """
  def action_assign(context):
    try:
      tlc = context.regpoint.get_top_level_class(location)
      if not getattr(tlc.RegistryMeta, 'multiple', False) and index > 0:
        raise EvaluationError("Attempted to use assign predicate with index > 0 on singular registry item '{0}'!".format(location)) 
    except registry_access.UnknownRegistryIdentifier:
      raise EvaluationError("Registry location '{0}' is invalid!".format(location))
    
    try:
      mdl = context.partial_config[location][index]
      for key, value in kwargs.iteritems():
        setattr(mdl, key, value)
    except (KeyError, IndexError):
      pass
    
    context.results.setdefault(location, []).append(registry_forms.AssignToFormAction(index, kwargs))
  
  return Action(action_assign)

def filter_cfg_items(cfg_items, _cls = None, _parent = None, **kwargs):
  """
  A helper function for filtering partial configuration items based on
  specified criteria.

  :param cfg_items: Partial configuration items
  :param _cls: Optional class name filter
  :param _parent: Optional parent instance filter
  :return: A tuple (indices, items)
  """
  indices = []
  items = []
  index = 0
  for cfg in cfg_items[:]:
    # Filter based on specified parent
    if _parent is not None and (not hasattr(cfg.__class__, '_registry_object_parent_link') or
                                getattr(cfg, cfg.__class__._registry_object_parent_link.name, None) != _parent):
      continue

    # Filter based on specified class name
    if _cls is not None and cfg.__class__.__name__ != _cls:
      index += 1
      continue

    # Filter based on partial values
    if kwargs:
      match = True
      for key, value in kwargs.iteritems():
        if not key.startswith('_') and getattr(cfg, key, None) != value:
          match = False
          break

      if not match:
        continue

    indices.append(index)
    items.append(cfg)
    index += 1

  return indices, items

def resolve_parent_item(context, parent):
  """
  A helper function for resolving the parent item in partial configuration.

  :param context: Rules evaluation context
  :param parent: Parent filter specified
  :return: Parent partial configuration item
  """
  parent_cfg = None
  if parent is not None:
    if '_item' not in parent:
      raise EvaluationError("Parent specifier must contain an '_item' entry!")

    cfg_items = context.partial_config.get(parent['_item'], [])
    item_index = parent.get('_index', 0)
    indices, items = filter_cfg_items(cfg_items, **parent)

    try:
      parent_cfg = items[item_index]
    except IndexError:
      raise EvaluationError("Specified parent index does not exist!")

  return parent_cfg

def remove(_item, _cls = None, _parent = None, **kwargs):
  """
  Action that removes specific configuration items.
  """
  def action_remove(context):
    try:
      tlc = context.regpoint.get_top_level_class(_item)
      if not getattr(tlc.RegistryMeta, 'multiple', False):
        raise EvaluationError("Attempted to use clear_config predicate on singular registry item '{0}'!".format(_item))
    except registry_access.UnknownRegistryIdentifier:
      raise EvaluationError("Registry location '{0}' is invalid!".format(_item))

    # Resolve parent item
    parent_cfg = resolve_parent_item(context, _parent)

    cfg_items = context.partial_config.get(_item, [])
    indices, items = filter_cfg_items(cfg_items, _cls, parent_cfg, **kwargs)
    for cfg in items:
      cfg_items.remove(cfg)

    if indices:
      context.results.setdefault(_item, []).append(registry_forms.RemoveFormAction(indices, parent = parent_cfg))
  
  return Action(action_remove)

def append(_item, _cls = None, _parent = None, **kwargs):
  """
  Action that appends a config item to a specific location.
  """
  def action_append(context):
    cls_name = _cls
    try:
      tlc = context.regpoint.get_top_level_class(_item)
      if not getattr(tlc.RegistryMeta, 'multiple', False):
        raise EvaluationError("Attempted to use append predicate on singular registry item '{0}'!".format(_item))
      if cls_name is None:
        cls_name = tlc._meta.module_name
    except registry_access.UnknownRegistryIdentifier:
      raise EvaluationError("Registry location '{0}' is invalid!".format(_item))
    
    # Resolve class name into the actual class
    cls = registry_access.get_model_class_by_name(cls_name)
    if not issubclass(cls, tlc):
      raise EvaluationError("Class '{0}' is not registered for '{1}'!".format(cls_name, _item))

    # Resolve parent item
    parent_cfg = resolve_parent_item(context, _parent)

    for key, value in kwargs.items():
      if callable(value):
        kwargs[key] = value(context)

    # Create the partial model and action
    mdl = registry_forms.create_config_item(cls, context.partial_config, kwargs, parent_cfg)
    context.results.setdefault(_item, []).append(registry_forms.AppendFormAction(mdl, parent_cfg))
  
  return Action(action_append)

def count(value):
  """
  Lazy value that returns the number of elements of another lazy expression.
  
  @param value: Lazy expression
  """
  if not isinstance(value, LazyValue):
    raise CompilationError("Count predicate argument must be a lazy value!")
  
  return LazyValue(lambda context: len(value(context) or []))

def router_descriptor(platform, router):
  """
  Lazy value that returns the router descriptor for the specified
  router.
  
  @param platform: Location of a platform identifier
  @param router: Location of a router identifier
  """
  class LazyRouterModel(LazyObject):
    def __init__(self, platform, model):
      self.__dict__['platform'] = platform
      self.__dict__['router'] = model
    
    def __call__(self, context):
      pass
    
    def __getattr__(self, key):
      def resolve_attribute(context):
        try:
          return getattr(cgm_base.get_platform(value(self.platform)(context)).get_router(value(self.router)(context)), key, None)
        except KeyError:
          return None
      
      return LazyValue(resolve_attribute, identifier = hashlib.md5(self.platform + self.router).hexdigest() + '-' + key)
    
    def __setattr__(self, key, value):
      raise AttributeError

  return LazyRouterModel(platform, router)

def value(location):
  """
  Lazy value that returns the result of a registry query.
  
  @param location: Registry location or LazyValue
  """
  if isinstance(location, LazyValue):
    return location
  
  def location_resolver(context):
    path, attribute = location.split('#') if '#' in location else (location, None)
    
    # First check the partial configuration store
    if path in context.partial_config and attribute is not None:
      obj = context.partial_config[path]
      if len(obj) > 1:
        raise EvaluationError("Path '%s' evaluates to a list but an attribute access is requested!" % path)
      
      try:
        return reduce(getattr, attribute.split('.'), obj[0])
      except:
        return None
    
    if context.root is None:
      return None
    obj = context.regpoint.get_accessor(context.root).by_path(path)
    
    if obj is None:
      return [] if attribute is None else None
    elif attribute is not None:
      if isinstance(obj, list):
        raise EvaluationError("Path '%s' evaluates to a list but an attribute access is requested!" % path)
      
      try:
        return reduce(getattr, attribute.split('.'), obj)
      except:
        return None
    else:
      return obj
  
  return LazyValue(location_resolver)

def changed(location):
  """
  A rule modifier predicate that will evaluate to True whenever a specific
  registry location has changed between rule evaluations.
  
  @param location: Registry location or LazyValue
  """
  return RuleModifier(
    lambda rule: setattr(rule, 'always_evaluate', True),
    lambda context: context.has_value_changed(location, value(location)(context))
  )

def foreach(container, *args):
  """
  A loop predicate that loops over the specified container and executes
  actions for each iteration. Current loop variable can be retrieved
  by using `loop_var`.

  Nesting of loops is currently not possible.

  :param container: Lazy container
  """
  if not isinstance(container, LazyValue):
    raise CompilationError("Foreach predicate container argument must be a lazy value!")

  def loop(context):
    for x in (container(context) or []):
      context._loop_variable = x
      for action in args:
        action(context)

  return Action(loop)

def loop_var():
  """
  Returns the value of the current loop variable when executed.
  """
  return LazyValue(lambda context: getattr(context, '_loop_variable', None))

def contains(container, value):
  """
  Contains predicate can be used to check if a specified lazy container
  contains a given value.

  :param container: Lazy container
  :param value: Value that should be checked
  """
  if not isinstance(container, LazyValue):
    raise CompilationError("Container argument must be a lazy value!")

  return LazyValue(lambda context: value in (container(context) or []))
