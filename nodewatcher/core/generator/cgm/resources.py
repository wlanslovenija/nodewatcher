from ....utils import ipaddr

class ResourceExhausted(Exception):
    pass

class ResourceAllocator(object):
    """
    The micro allocations class is used to track resource allocations
    between CGMs.
    """
    def __init__(self):
        """
        Class constructor.
        """
        self.resources = {}

    def add(self, resource):
        """
        Adds another resource that can be used for allocations.
        """
        self.resources.setdefault(resource.__class__, []).append(resource)

    def get(self, resource_cls, **kwargs):
        """
        Attempts to get an allocation of the specified resource.

        :param resource_cls: Resource class
        """
        try:
            resources = self.resources[resource_cls]
            for resource in resources:
                try:
                    return resource.allocate(**kwargs)
                except ResourceExhausted:
                    continue

            raise ResourceExhausted
        except KeyError:
            raise ResourceExhausted

class Resource(object):
    """
    Abstract resource.
    """
    def allocate(self, **kwargs):
        """
        Allocates one instance of this resource.
        """
        raise NotImplementedError

class IpResource(Resource):
    """
    An IP subnet resource.
    """
    def __init__(self, family, subnet, config):
        """
        Class constructor.

        :param family: Address family
        :param subnet: Subnet to allocate from
        :param config: Configuration object this resource has been
          created from
        """
        self.family = family
        self.subnet = subnet
        self.config = config
        self.allocation = self.subnet.iterhosts()

    def allocate(self, family = None):
        """
        Allocates the next host on the list.
        """
        if family is not None and family != self.family:
            raise ResourceExhausted

        try:
            return ipaddr.IPNetwork("%s/%d" % (self.allocation.next(), self.subnet.prefixlen))
        except StopIteration:
            raise ResourceExhausted
