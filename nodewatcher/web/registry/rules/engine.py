import copy

__all__ = [
  'EngineContext',
  'Rule',
  'RuleModifier',
  'Action',
  'LazyObject',
  'LazyValue',
  'CompilationError',
  'EvaluationError',
]

class CompilationError(Exception):
  pass

class EvaluationError(Exception):
  pass

class LazyObject(object):
  def __call__(self, context):
    raise NotImplementedError

class Rule(LazyObject):
  always_evaluate = False
  
  def __init__(self, condition, actions):
    self.condition = condition
    self.actions = actions
  
  def __call__(self, context):
    if isinstance(self.condition, RuleModifier):
      self.condition.modifier(self)
    
    condition = self.condition(context)
    if not isinstance(condition, bool):
      raise EvaluationError("Condition does not evaluate into a boolean value!")
    
    context.mark(self, condition)
    if condition == False:
      return
    
    changed = context.has_changed(self)
    for idx, action in enumerate(self.actions):
      if isinstance(action, Action) and changed:
        action(context)
      elif isinstance(action, Rule):
        context.enter_sublevel("rule" + str(idx))
        action(context)
        context.leave_sublevel()

class LazyValue(LazyObject):
  def __init__(self, op):
    self.op = op
  
  def __lt__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) < other)
  
  def __le__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) <= other)
  
  def __eq__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) == other)
  
  def __ne__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) != other)
  
  def __gt__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) > other)
  
  def __ge__(self, other):
    other = other(context) if isinstance(other, LazyValue) else other
    return LazyValue(lambda context: self(context) >= other)
  
  def __call__(self, context):
    return self.op(context)

class RuleModifier(LazyObject):
  def __init__(self, modifier, condition):
    self.modifier = modifier
    self.condition = condition
  
  def __call__(self, context):
    return self.condition(context)

class Action(LazyObject):
  def __init__(self, op):
    self.op = op
  
  def __call__(self, context):
    self.op(context)

class EngineContext(object):
  def __init__(self, state = None):
    self.state = state or {}
    self.new_state = copy.deepcopy(self.state)
    self._levels = []
    self._rules = []
  
  def run(self, node):
    self.node = node
    self.results = []
    for idx, rule in enumerate(self._rules):
      self.enter_sublevel("rule" + str(idx))
      rule(self)
      self.leave_sublevel()
    
    # TODO encode self.new_state in self.results
  
  def enter_sublevel(self, name):
    self._levels.append(name)
  
  def leave_sublevel(self):
    self._levels.pop()
  
  def current_level(self):
    return ".".join(self._levels)
  
  def mark(self, rule, value):
    self.new_state[':' + self.current_level()] = value
  
  def has_changed(self, rule):
    if rule.always_evaluate:
      return True
    
    return self.state.get(':' + self.current_level(), False) != self.new_state[':' + self.current_level()]
  
  def has_value_changed(self, location, value):
    old_value = self.state.get(location)
    if old_value is None:
      return True
    
    if old_value == value:
      return False
    
    self.new_state[location] = value
    return True

