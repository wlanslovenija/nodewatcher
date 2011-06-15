import hashlib
import inspect

from web.registry import access as registry_access
from web.registry import forms as registry_forms
from web.registry.rules.engine import *
from web.registry.cgm import base as cgm_base 

# Exports
__all__ = [
  'rule',
  'value',
  'router_descriptor',
  'count',
  'changed',
  'assign',
  'clear_config',
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

def clear_config(location):
  """
  Action that clears all config items for a specific location.
  
  @param location: Registry location
  """
  def action_clear_config(context):
    try:
      tlc = context.regpoint.get_top_level_class(location)
      if not getattr(tlc.RegistryMeta, 'multiple', False):
        raise EvaluationError("Attempted to use clear_config predicate on singular registry item '{0}'!".format(location)) 
    except registry_access.UnknownRegistryIdentifier:
      raise EvaluationError("Registry location '{0}' is invalid!".format(location))
    
    context.partial_config[location] = []
    context.results.setdefault(location, []).append(registry_forms.ClearFormsAction())
  
  return Action(action_clear_config)

def append(location, **kwargs):
  """
  Action that appends a config item to a specific location.
  
  @param location: Registry location
  """
  def action_append(context):
    if '[' in location:
      loc, cls_name = location.split('[')
      cls_name = cls_name[:-1].lower()
    else:
      loc = location
      cls_name = None
    
    try:
      tlc = context.regpoint.get_top_level_class(loc)
      if not getattr(tlc.RegistryMeta, 'multiple', False):
        raise EvaluationError("Attempted to use append predicate on singular registry item '{0}'!".format(loc))
      if cls_name is None:
        cls_name = tlc._meta.module_name 
    except registry_access.UnknownRegistryIdentifier:
      raise EvaluationError("Registry location '{0}' is invalid!".format(loc))
    
    # Resolve class name into the actual class
    cls = registry_access.get_model_class_by_name(cls_name)
    if not issubclass(cls, tlc):
      raise EvaluationError("Class '{0}' is not registered for '{1}'!".format(cls_name, loc))
    
    try:
      mdl = cls()
      for key, value in kwargs.iteritems():
        setattr(mdl, key, value)
      context.partial_config[location].append(mdl)
    except KeyError:
      pass
    
    context.results.setdefault(location, []).append(registry_forms.AppendFormAction(cls, kwargs))
  
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

