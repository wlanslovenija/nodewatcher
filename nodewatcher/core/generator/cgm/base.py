from ....utils import loader

from ...registry import registration

from . import devices as cgm_devices, resources as cgm_resources

# Registered platform modules
PLATFORM_REGISTRY = {}


class ValidationError(Exception):
    pass


class BuildError(Exception):
    pass


class PlatformConfiguration(object):
    """
    A flexible in-memory platform configuration store that is used
    by modules to make modifications and perform configuration. The
    default implementation only contains some platform-independent
    methods.
    """

    def __init__(self):
        """
        Class constructor.
        """

        self.resources = cgm_resources.ResourceAllocator()
        self.packages = set()

    def __getstate__(self):
        self.__dict__.pop('resources', None)
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


class PlatformBase(object):
    """
    An abstract base class for all platform implementations.
    """

    config_class = PlatformConfiguration

    def __init__(self):
        """
        Class constructor.
        """

        self.name = None
        self._modules = []
        self._packages = []
        self._devices = {}

    def generate(self, node):
        """
        Generates a concrete configuration for this platform.
        """

        cfg = self.config_class()

        # Execute the module chain in order
        for _, module, device in sorted(self._modules):
            if device is None or device == node.config.core.general().router:
                module(node, cfg)

        # Process user-configured packages
        for name, cfgclass, package in self._packages:
            pkgcfg = node.config.core.packages(onlyclass=cfgclass)
            if [x for x in pkgcfg if x.enabled]:
                package(node, pkgcfg, cfg)
                cfg.packages.add(name)

        return cfg

    def build(self, node, cfg):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param node: Node instance to build the firmware for
        :param cfg: Generated configuration (platform-dependent)
        :return: A list of generated firmware files
        """

        raise NotImplementedError

    def defer_build(self, node, cfg):
        """
        Deferrs formatting and building to a background Celery job. The job
        is responsible for calling proper format and build methods on this
        platform.

        :param node: Node instance to generate the firmware for
        :param cfg: Generated configuration (platform-dependent)
        """

        from . import tasks
        tasks.background_build.delay(node, self.name, cfg)

    def register_module(self, weight, module, device=None):
        """
        Registers a new platform module.

        :param weight: Call order weight
        :param module: Module implementation function
        :param device: Optional device identifier
        """

        if [x for x in self._modules if x[1] == module]:
            return

        self._modules.append((weight, module, device))

    def register_package(self, name, config, package):
        """
        Registers a new platform package.

        :param name: Platform-dependent package name
        :param config: Configuration class
        :param package: Package implementation function
        """

        if [x for x in self._packages if x[2] == package]:
            return

        self._packages.append((name, config, package))

    def register_device(self, device):
        """
        Registers a new device with this platform.

        :param device: A subclass of DeviceBase
        """

        if not issubclass(device, cgm_devices.DeviceBase):
            raise TypeError("Router descriptor must be a subclass of DeviceBase!")

        self._devices[device.identifier] = device
        device.register(self)

    def get_device(self, device):
        """
        Returns a device descriptor.

        :param device: Unique device identifier
        """

        return self._devices[device]


def register_platform(enum, text, platform):
    """
    Registers a new platform with the Configuration Generation Modules
    system.
    """

    if not isinstance(platform, PlatformBase):
        raise TypeError("Platform formatter/builder implementation must be a PlatformBase instance!")

    if enum in PLATFORM_REGISTRY:
        raise ValueError("Platform '{0}' is already registered!".format(enum))

    PLATFORM_REGISTRY[enum] = platform
    platform.name = enum

    # Register the choice in configuration registry
    registration.point("node.config").register_choice("core.general#platform", registration.Choice(enum, text))


def get_platform(platform):
    """
    Returns the given platform implementation.
    """

    try:
        return PLATFORM_REGISTRY[platform]
    except KeyError:
        raise KeyError("Platform '{0}' does not exist!".format(platform))


def register_platform_module(platform, weight=999, device=None):
    """
    Registers a new platform module.
    """

    def wrapper(f):
        get_platform(platform).register_module(weight, f, device=device)
        return f

    return wrapper


def register_platform_package(platform, name, cfgclass):
    """
    Registers a new platform package.
    """

    def wrapper(f):
        get_platform(platform).register_package(name, cfgclass, f)
        return f

    return wrapper


def register_device(platform, device):
    """
    Registers a new device.
    """

    get_platform(platform).register_device(device)


def iterate_devices():
    """
    Iterates over all registered devices.
    """

    for platform in PLATFORM_REGISTRY.values():
        for device in platform._devices.values():
            yield device


def generate_config(node, only_validate=False):
    """
    Generates configuration and/or firmware for the specified node.

    :param node: Node instance
    :param only_validate: True if only validation should be performed
    """

    # Ensure that all CGMs are registred
    loader.load_modules('cgm')

    # Determine the destination platform
    try:
        platform = get_platform(node.config.core.general().platform)
    except (AttributeError, KeyError):
        return None

    cfg = platform.generate(node)
    if not only_validate:
        platform.defer_build(node, cfg)

    return cfg
