class SerializerException(Exception):
    pass


class SerializerAlreadyRegistered(SerializerException):
    pass


class SerializerNotRegistered(SerializerException):
    pass
