import inspect

from registry.rules.engine import * 

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
  if not isinstance(condition, (LazyValue, RuleModifier)):
    raise CompilationError("Rule conditions must be lazy values or rule modifiers!")
  
  ctx = inspect.stack()[1][0].f_locals.get('ctx')
  if not isinstance(ctx, EngineContext):
    raise CompilationError("Expecting engine context as 'ctx' variable in parent local scope!")
  
  for x in args:
    if not isinstance(x, (Action, Rule)):
      raise CompilationError("Rule actions must be Action or Rule instances!")
    
    if isinstance(x, Rule):
      ctx._rules.remove(x)
  
  new_rule = Rule(condition, args)
  ctx._rules.append(new_rule)
  return new_rule

def assign(location, index = 0, **kwargs):
  # TODO location validation
  def action_assign(context):
    values = []
    for field, value in kwargs.iteritems():
      values.append('{0}: "{1}"'.format(field, str(value).replace('\\', '\\\\')))
    values = ",".join(values)
    context.results.append('registry.assign("{0}", {1}, {{ {2} }});'.format(location, index, values))
  
  return Action(action_assign)

def clear_config(location):
  # TODO location validation
  def action_clear_config(context):
    context.results.append('registry.clear_config("{0}");'.format(location))
  
  return Action(action_clear_config)

def append(location, **kwargs):
  # TODO location validation
  def action_append(context):
    values = []
    for field, value in kwargs.iteritems():
      values.append('{0}: "{1}"'.format(field, str(value).replace('\\', '\\\\')))
    values = ",".join(values)
    context.results.append('registry.append("{0}", {{ {1} }});'.format(location, values))
  
  return Action(action_append)

def count(value):
  return LazyValue(lambda context: len(value(context)))

def value(location):
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
  return RuleModifier(
    lambda rule: setattr(rule, 'always_evaluate', True),
    lambda context: context.has_value_changed(location, value(location)(context))
  )

