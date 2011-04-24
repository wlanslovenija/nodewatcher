from django.conf import settings
from django.utils import importlib

# Exports
__all__ = [
  'evaluate'
]

def evaluate(node):
  """
  Evaluates the rules.
  
  @param node: Node to evaluate the rules for
  """
  try:
    rules = importlib.import_module(settings.REGISTRY_RULES_MODULE)
    rules.ctx.run(node)
  except Exception, e:
    return ['registry.error("{0}");'.format(e.args[0])]
  
  return rules.ctx.results

