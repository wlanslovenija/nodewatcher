

class BuilderConnectionFailed(Exception):
    """
    Exception that gets raised when connection with the builder fails.
    """

    pass


class MalformedPrivateKey(Exception):
    """
    Exception that gets raised when the specified private key is malformed.
    """

    pass
