class TopologyAttributeException(Exception):
    pass


class InvalidTopologyAttribute(TopologyAttributeException):
    pass


class TopologyAttributeAlreadyRegistered(TopologyAttributeException):
    pass


class TopologyAttributeNotRegistered(TopologyAttributeException):
    pass
