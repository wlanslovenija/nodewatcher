from frontend.registry.rules import engine
from frontend.registry.rules.predicates import *

# Inject the engine context into the rule scope so it will be found by rule
# predicates
ctx = engine.EngineContext()

