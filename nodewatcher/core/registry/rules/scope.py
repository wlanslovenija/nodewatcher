from nodewatcher.core.registry.rules import engine
from nodewatcher.core.registry.rules.predicates import *

# Inject the engine context into the rule scope so it will be found by rule
# predicates
ctx = engine.EngineContext()
