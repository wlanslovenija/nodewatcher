from django.conf import settings
from django.utils import importlib

# Exports
__all__ = [
  'evaluate'
]

def evaluate(node, state, partial_config = None):
  """
  Evaluates the rules.
  
  @param node: Node to evaluate the rules for
  @param state: Current evaluation state
  @param partial_config: Optional partial updated configuration
  """
  if partial_config is None:
    partial_config = {}
  
  try:
    rules = importlib.import_module(settings.REGISTRY_RULES_MODULE)
    rules.ctx.run(node, state, partial_config)
  except Exception, e:
    return ['registry.error("{0}");'.format(e.args[0])]
  
  return rules.ctx.results

