import copy
import json

# Exports
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
  """
  Exceptions that get raised at rule compile time.
  """
  pass

class EvaluationError(Exception):
  """
  Exceptions that get raised while evaluating rules.
  """
  pass

class LazyObject(object):
  """
  Represents a callable object that is used for lazy evaluation.
  """
  def __call__(self, context):
    """
    Subclasses must implement this method to evaluate the object.
    
    @param context: Evaluation context (EngineContext instance)
    """
    raise NotImplementedError

class Rule(LazyObject):
  """
  A rule that can be evaluated.
  """
  # Set to true to evaluate the rule even when condition is unchanged from
  # last rule evaluation
  always_evaluate = False
  
  def __init__(self, condition, actions):
    """
    Class constructor.
    
    @param condition: A lazy expression
    @param actions: A list of actions
    """
    self.condition = condition
    self.actions = actions
  
  def __call__(self, context):
    """
    Evaluates the rule.
    """
    if isinstance(self.condition, RuleModifier):
      self.condition.modifier(self)
    
    condition = self.condition(context)
    if not isinstance(condition, bool):
      raise EvaluationError("Condition does not evaluate into a boolean value!")
    
    # Remember condition value so we don't reevaluate rules unless conditions change
    context.mark(self, condition)
    if condition == False:
      return
    
    # Evaluate all subrules and execute subactions when something has changed
    changed = context.has_changed(self)
    for idx, action in enumerate(self.actions):
      if isinstance(action, Action) and changed:
        action(context)
      elif isinstance(action, Rule):
        context.enter_sublevel("rule" + str(idx))
        action(context)
        context.leave_sublevel()

class LazyValue(LazyObject):
  """
  An abstract lazy value that can be used for building lazy expressions.
  """ 
  def __init__(self, op, identifier = None):
    """
    Class constructor.
    
    @param op: A callable operation
    @param identifier: Optional identifier
    """
    self.op = op
    self.identifier = identifier
  
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
    """
    Evaluates the value.
    """
    return self.op(context)
  
  def __str__(self):
    return self.identifier or "<LazyValue>"

class RuleModifier(LazyObject):
  """
  Rule modifier is a special object that can be used as a rule condition and
  can modify rule's properties before the condition is evaluated.
  """
  def __init__(self, modifier, condition):
    """
    Class constructor.
    
    @param modifier: A callable that may modify the rule
    @param condition: A lazy expression that is the condition
    """
    self.modifier = modifier
    self.condition = condition
  
  def __call__(self, context):
    """
    Evaluates the condition.
    """
    return self.condition(context)

class Action(LazyObject):
  """
  Actions are callables that are executed in case a rule's condition is satisified
  and the condition has changed.
  """
  def __init__(self, op):
    """
    Class constructor.
    
    @param op: A callable that gets executed for this action
    """
    self.op = op
  
  def __call__(self, context):
    """
    Executes this action.
    """
    self.op(context)

class EngineContext(object):
  """
  Engine context holds state for a particular evaluation.
  """
  def __init__(self, state = None):
    """
    Class constructor.
    
    @param state: Old state dictionary
    """
    self._levels = []
    self._rules = []
  
  def run(self, regpoint, root, state, partial_config):
    """
    Evaluates rules on a specific regpoint root object.
    
    @param regpoint: Registration point instance
    @param root: Regpoint root object to evaluate the rules on
    @param state: Current evaluation state
    @param partial_config: Optional partial updated configuration
    """
    self.regpoint = regpoint
    self.root = root
    self.state = state or {}
    self.new_state = copy.deepcopy(self.state)
    self.partial_config = partial_config
    self.results = {}
    for idx, rule in enumerate(self._rules):
      self.enter_sublevel("rule" + str(idx))
      rule(self)
      self.leave_sublevel()
    
    self.results['STATE'] = self.new_state
  
  def enter_sublevel(self, name):
    """
    Enters a sublevel in the rules hierarchy.
    """
    self._levels.append(name)
  
  def leave_sublevel(self):
    """
    Leaves the current sublevel in the rules hierarchy.
    """
    self._levels.pop()
  
  def current_level(self):
    """
    Returns an identifier that represents the current sublevel.
    """
    return ".".join(self._levels)
  
  def mark(self, rule, value):
    """
    Marks current rule's condition evaluation result for later comparison.
    
    @param rule: Rule instance
    @param value: Condition evaluation result
    """
    self.new_state[':' + self.current_level()] = value
  
  def has_changed(self, rule):
    """
    Returns True if current rule's condition evaluation result has changed
    since last evaluation.
    
    @param rule: Rule instance
    @return: True if the condition evaluation result has changed
    """
    if rule.always_evaluate:
      return True
    
    return self.state.get(':' + self.current_level(), False) != self.new_state[':' + self.current_level()]
  
  def has_value_changed(self, location, value):
    """
    Returns True if some registry value has changed since last evaluation.
    
    @param location: Registry location
    @param value: New registry value
    """
    location = str(location)
    old_value = self.state.get(location)
    if old_value is None:
      return True
    
    if old_value == value:
      return False
    
    self.new_state[location] = value
    return True

