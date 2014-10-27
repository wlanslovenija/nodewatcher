from nodewatcher.core.monitor import models as monitor_models


class TopologyAttribute(object):
    @classmethod
    def get_lookup_key(cls, **kwargs):
        raise NotImplementedError

    def get_self_lookup_key(self):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError


class NodeAttribute(TopologyAttribute):
    def __init__(self, name, field, transform=None):
        """
        Class constructor.

        :param name: Unique name used for storage in the topology
        :param field: Registry field reference (eg. 'core.general#name')
        :param transform: Optional value transformation callable
        """

        self.name = name
        self.field = field
        self.transform = transform

    @classmethod
    def get_lookup_key(cls, **kwargs):
        return ("node",)

    def get_self_lookup_key(self):
        return self.get_lookup_key()

    def get_name(self):
        return self.name


class LinkAttribute(TopologyAttribute):
    def __init__(self, link_class, name, value):
        """
        Class constructor.

        :param link_class: Topology link class
        :param name: Unique name for storage in the topology
        :param value: Constant value or callable
        """

        if not issubclass(link_class, monitor_models.TopologyLink):
            raise TypeError('Topology link class must be a subclass of nodewatcher.core.monitor.models.TopologyLink!')

        self.link_class = link_class
        self.name = name
        self.value = value

    @classmethod
    def get_lookup_key(cls, link_class, **kwargs):
        return ("link", link_class)

    def get_self_lookup_key(self):
        return self.get_lookup_key(link_class=self.link_class)

    def get_name(self):
        return self.name
