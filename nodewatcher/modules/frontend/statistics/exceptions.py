class StatisticsResourceException(Exception):
    pass


class InvalidStatisticsResource(StatisticsResourceException):
    pass


class StatisticsResourceAlreadyRegistered(StatisticsResourceException):
    pass


class StatisticsResourceNotRegistered(StatisticsResourceException):
    pass
