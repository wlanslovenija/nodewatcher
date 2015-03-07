from django.conf import settings
from django.utils import importlib

# Exports
__all__ = [
    'evaluate'
]


def evaluate(regpoint, root, form_state, state=None):
    """
    Evaluates the rules.

    :param regpoint: Registration point instance
    :param root: Regpoint root instance to evaluate the rules for
    :param state: Optional current evaluation state
    :param form_state: Optional form state
    """

    if state is None:
        state = {}

    rules_module = settings.REGISTRY_RULES_MODULES.get(regpoint.name, None)
    if rules_module is not None:
        rules = importlib.import_module(rules_module)
        rules.ctx.run(regpoint, root, state, form_state)
        return rules.ctx.new_state

    return {}
