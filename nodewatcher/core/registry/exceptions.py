

class RegistryException(Exception):
    pass


class UnknownRegistryIdentifier(RegistryException):
    pass


class UnknownRegistryClass(RegistryException):
    pass
