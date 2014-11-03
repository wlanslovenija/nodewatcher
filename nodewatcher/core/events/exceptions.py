

class EventException(Exception):
    pass


class InvalidEventSink(EventException, TypeError):
    pass


class InvalidEventRecord(EventException, TypeError):
    pass


class EventSinkAlreadyRegistered(EventException):
    pass


class EventRecordAlreadyRegistered(EventException):
    pass


class EventSinkNotRegistered(EventException):
    pass


class EventRecordNotRegistered(EventException):
    pass


class EventFilterNotFound(EventException):
    pass


class EventFilterAlreadyAttached(EventException):
    pass


class InvalidEventFilter(EventException, TypeError):
    pass


class FilterArgumentReserved(EventException):
    pass
