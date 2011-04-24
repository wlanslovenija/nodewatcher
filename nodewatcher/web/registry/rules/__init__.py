from django.conf import settings
from django.utils import importlib

__all__ = [
  'evaluate'
]

def evaluate(node):
  """
  Evaluates the rules.
  """
  rules = importlib.import_module(settings.REGISTRY_RULES_MODULE)
  rules.ctx.run(node)
  return rules.ctx.results

