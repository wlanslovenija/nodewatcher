class StreamDescriptorException(Exception):
    pass


class StreamDescriptorAlreadyRegistered(StreamDescriptorException):
    pass


class StreamDescriptorNotRegistered(StreamDescriptorException):
    pass


class StreamDescriptorHasInvalidBase(StreamDescriptorException):
    pass
