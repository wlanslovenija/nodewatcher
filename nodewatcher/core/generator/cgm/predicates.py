import hashlib

from ...registry.rules.engine import *
from ...registry.rules.predicates import value
from . import base as cgm_base

# Exports
__all__ = [
    'router_descriptor',
]

def router_descriptor(platform, router):
    """
    Lazy value that returns the router descriptor for the specified
    router.

    :param platform: Location of a platform identifier
    :param router: Location of a router identifier
    """

    class LazyRouterModel(LazyObject):
        def __init__(self, platform, model):
            self.__dict__['platform'] = platform
            self.__dict__['router'] = model

        def __call__(self, context):
            pass

        def __getattr__(self, key):
            def resolve_attribute(context):
                try:
                    return getattr(cgm_base.get_platform(value(self.platform)(context)).get_router(value(self.router)(context)), key, None)
                except KeyError:
                    return None

            return LazyValue(resolve_attribute, identifier = hashlib.md5(self.platform + self.router).hexdigest() + '-' + key)

        def __setattr__(self, key, value):
            raise AttributeError

    return LazyRouterModel(platform, router)
