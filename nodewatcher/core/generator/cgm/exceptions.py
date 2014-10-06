

class NoBuildChannelsConfigured(Exception):
    """
    Exception that gets raised when no build channels are configured.
    """

    pass


class NoBuildersConfigured(Exception):
    """
    Exception that gets raised when no builders are configured.
    """

    pass


class NoSuitableBuildersFound(Exception):
    """
    Exception that gets raised when no suitable builders for building for the
    specified platform and architecture are found.
    """

    pass


class BuildError(Exception):
    """
    Exception that gets raised when a build error occurrs.
    """

    pass
