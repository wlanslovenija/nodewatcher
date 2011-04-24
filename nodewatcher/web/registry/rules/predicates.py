import inspect

from registry import access as registry_access
from registry.rules.engine import * 

# Exports
__all__ = [
  'rule',
  'value',
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
  try:
    tlc = registry_access.get_class_by_path(location)
    if not getattr(tlc.RegistryMeta, 'multiple', False) and index > 0:
      raise CompilationError("Attempted to use assign predicate with index > 0 on singular registry item '{0}'!".format(location)) 
  except registry_access.UnknownRegistryIdentifier:
    raise CompilationError("Registry location '{0}' is invalid!".format(location))
  
  def action_assign(context):
    values = []
    for field, value in kwargs.iteritems():
      values.append('{0}: "{1}"'.format(field, str(value).replace('\\', '\\\\')))
    values = ",".join(values)
    context.results.append('registry.assign("{0}", {1}, {{ {2} }});'.format(location, index, values))
  
  return Action(action_assign)

def clear_config(location):
  """
  Action that clears all config items for a specific location.
  
  @param location: Registry location
  """
  try:
    tlc = registry_access.get_class_by_path(location)
    if not getattr(tlc.RegistryMeta, 'multiple', False):
      raise CompilationError("Attempted to use clear_config predicate on singular registry item '{0}'!".format(location)) 
  except registry_access.UnknownRegistryIdentifier:
    raise CompilationError("Registry location '{0}' is invalid!".format(location))
  
  def action_clear_config(context):
    context.results.append('registry.clear_config("{0}");'.format(location))
  
  return Action(action_clear_config)

def append(location, **kwargs):
  """
  Action that appends a config item to a specific location.
  
  @param location: Registry location
  """
  try:
    tlc = registry_access.get_class_by_path(location)
    if not getattr(tlc.RegistryMeta, 'multiple', False):
      raise CompilationError("Attempted to use append predicate on singular registry item '{0}'!".format(location)) 
  except registry_access.UnknownRegistryIdentifier:
    raise CompilationError("Registry location '{0}' is invalid!".format(location))
  
  def action_append(context):
    values = []
    for field, value in kwargs.iteritems():
      values.append('{0}: "{1}"'.format(field, str(value).replace('\\', '\\\\')))
    values = ",".join(values)
    context.results.append('registry.append("{0}", {{ {1} }});'.format(location, values))
  
  return Action(action_append)

def count(value):
  """
  Lazy value that returns the number of elements of another lazy expression.
  
  @param value: Lazy expression
  """
  if not isinstance(value, LazyValue):
    raise CompilationError("Count predicate argument must be a lazy value!")
  
  return LazyValue(lambda context: len(value(context)))

def value(location):
  """
  Lazy value that returns the result of a registry query.
  
  @param location: Registry location (may contain attributes)
  """
  def location_resolver(context):
    path, attribute = location.split('#') if '#' in location else (location, None)
    obj = context.node.config.by_path(path)
    
    if obj is None:
      return [] if attribute is None else None
    elif attribute is not None:
      if isinstance(obj, list):
        raise EvaluationError("Path '%s' evaluates to a list but an attribute access is requested!" % path)
      
      try:
        return reduce(getattr, attribute.split('.'), obj)
      except AttributeError:
        return None
    else:
      return obj
  
  return LazyValue(location_resolver)

def changed(location):
  """
  A rule modifier predicate that will evaluate to True whenever a specific
  registry location has changed between rule evaluations.
  
  @param location: Registry location (may contain attributes)
  """
  return RuleModifier(
    lambda rule: setattr(rule, 'always_evaluate', True),
    lambda context: context.has_value_changed(location, value(location)(context))
  )

