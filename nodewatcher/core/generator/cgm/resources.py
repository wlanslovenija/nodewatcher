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

        # Special handling for single-address subnets where we can only allocate
        # that one address (in this case network/broadcast is ignored)
        if self.subnet.numhosts == 1:
            self.allocation = iter([self.subnet.network])
        else:
            self.allocation = self.subnet.iterhosts()

    def allocate(self, family=None):
        """
        Allocates the next host on the list.
        """

        if family is not None and family != self.family:
            raise ResourceExhausted

        try:
            return ipaddr.IPNetwork("%s/%d" % (self.allocation.next(), self.subnet.prefixlen))
        except StopIteration:
            raise ResourceExhausted


class PhysicalPortResource(Resource):
    """
    A phsyical port resource.
    """

    def __init__(self, port_type, ports):
        """
        Class constructor.

        :param ports: A list of available physical ports
        :param port_type: Arbitrary string identifying the port type
        """

        self.port_type = port_type
        self.available_ports = set(ports)
        self.allocated_ports = set()

    def allocate(self, port, port_type=None):
        """
        Allocates a specific port.
        """

        if port_type is not None and port_type != self.port_type:
            raise ResourceExhausted

        print 'allocating port', port

        try:
            self.available_ports.remove(port)
        except KeyError:
            raise ResourceExhausted

        self.allocated_ports.add(port)

        return port
