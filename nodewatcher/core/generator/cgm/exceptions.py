

class BuilderConfigurationError(Exception):
    pass


class NoBuildChannelsConfigured(BuilderConfigurationError):
    """
    Exception that gets raised when no build channels are configured.
    """

    pass


class NoBuildersConfigured(BuilderConfigurationError):
    """
    Exception that gets raised when no builders are configured.
    """

    pass


class NoSuitableBuildersFound(BuilderConfigurationError):
    """
    Exception that gets raised when no suitable builders for building for the
    specified platform and architecture are found.
    """

    pass


class NoDeviceConfigured(BuilderConfigurationError):
    """
    Exception that gets raised when no device is configured.
    """

    pass


class BuildError(Exception):
    """
    Exception that gets raised when a build error occurrs.
    """

    pass
