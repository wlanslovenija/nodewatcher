from . import engine

# Import predicates into the namespace so that they are available directly
from .predicates import *

# Inject the engine context into the rule scope so it will be found by rule predicates
ctx = engine.EngineContext()
