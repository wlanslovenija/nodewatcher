
class EventException(Exception):
    pass

class EventSinkNotFound(EventException):
    pass

class InvalidEventSink(EventException, TypeError):
    pass

class EventFilterNotFound(EventException):
    pass

class InvalidEventFilter(EventException, TypeError):
    pass
