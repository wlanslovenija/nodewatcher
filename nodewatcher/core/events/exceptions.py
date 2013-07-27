

class EventException(Exception):
    pass


class InvalidEventSink(EventException, TypeError):
    pass


class EventSinkAlreadyRegistered(EventException):
    pass


class EventSinkNotRegistered(EventException):
    pass


class EventFilterNotFound(EventException):
    pass


class InvalidEventFilter(EventException, TypeError):
    pass
