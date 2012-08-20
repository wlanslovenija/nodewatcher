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

def get_cfg_indices(cfg_items, _cls = None, **kwargs):
  """
  A helper method for filtering partial configuration items based on
  specified criteria.
  """
  indices = []
  for idx, cfg in enumerate(cfg_items[:]):
    # Filter based on specified class name
    if _cls is not None and cfg.__class__.__name__ != _cls:
      continue

    # Filter based on partial values
    if kwargs:
      match = True
      for key, value in kwargs.iteritems():
        if getattr(cfg, key, None) != value:
          match = False
          break

      if not match:
        continue

    indices.append(idx)

  return indices

def remove(_item, _cls = None, **kwargs):
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

    cfg_items = context.partial_config.get(_item, [])
    indices = get_cfg_indices(cfg_items, _cls, **kwargs)
    for cfg in [cfg_items[i] for i in indices]:
      cfg_items.remove(cfg)

    if indices:
      context.results.setdefault(_item, []).append(registry_forms.RemoveFormAction(indices))
  
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

    try:
      mdl = cls()
      for key, value in kwargs.items():
        if callable(value):
          value = value(context)
          kwargs[key] = value

        setattr(mdl, key, value)
      context.partial_config[_item].append(mdl)
    except KeyError:
      pass
    
    context.results.setdefault(_item, []).append(registry_forms.AppendFormAction(cls, kwargs))
  
  return Action(action_append)

def count(value):
  """
  Lazy value that returns the number of elements of another lazy expression.
  
  @param value: Lazy expression
  """
  if not isinstance(value, LazyValue):
    raise CompilationError("Count predicate argument must be a lazy value!")
  
  return LazyValue(lambda context: len(value(context)))

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
