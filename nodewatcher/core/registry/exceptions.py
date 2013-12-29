

class RegistryException(Exception):
    pass


class RegistryItemAlreadyRegistered(RegistryException):
    pass


class RegistryItemNotRegistered(RegistryException):
    pass


class InvalidRegistryItemName(RegistryException):
    pass


class UnknownRegistryClass(RegistryException):
    pass
