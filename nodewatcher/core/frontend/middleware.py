class ClientNodeMiddleware(object):
    """
    Adds ``node`` attribute to ``request`` with the node the client is connected to.

    Set to ``None`` if client is not coming from the network.
    """

    def process_request(self, request):
        # TODO: Implement
        request.node = None
