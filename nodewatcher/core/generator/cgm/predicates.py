import hashlib

from ...registry.rules import engine
from ...registry.rules.predicates import value

from . import base as cgm_base

# Exports
__all__ = [
    'device_descriptor',
]


def device_descriptor(platform, device):
    """
    Lazy value that returns the device descriptor for the specified
    device.

    :param platform: Location of a platform identifier
    :param device: Location of a device identifier
    """

    class LazyDeviceModel(engine.LazyObject):
        def __init__(self, platform, model):
            self.__dict__['platform'] = platform
            self.__dict__['device'] = model

        def __call__(self, context):
            pass

        def __getattr__(self, key):
            def resolve_attribute(context):
                try:
                    return getattr(cgm_base.get_platform(value(self.platform)(context)).get_device(value(self.device)(context)), key, None)
                except KeyError:
                    return None

            return engine.LazyValue(resolve_attribute, identifier=hashlib.md5(self.platform + self.device).hexdigest() + '-' + key)

        def __setattr__(self, key, value):
            raise AttributeError

    return LazyDeviceModel(platform, device)
