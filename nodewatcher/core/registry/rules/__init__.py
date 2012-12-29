from django.conf import settings
from django.utils import importlib

# Exports
__all__ = [
    'evaluate'
]

def evaluate(regpoint, root, state, partial_config = None):
    """
    Evaluates the rules.

    :param regpoint: Registration point instance
    :param root: Regpoint root instance to evaluate the rules for
    :param state: Current evaluation state
    :param partial_config: Optional partial updated configuration
    """

    if partial_config is None:
        partial_config = {}

    rules_module = settings.REGISTRY_RULES_MODULES.get(regpoint.name, None)
    if rules_module is not None:
        rules = importlib.import_module(rules_module)
        rules.ctx.run(regpoint, root, state, partial_config)
        return rules.ctx.results

    return {'STATE': {}}
