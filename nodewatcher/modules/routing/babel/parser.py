import radix
import socket
import telnetlib


class BabelParseFailed(Exception):
    pass


class BabelParser(object):
    """
    Parser for babeld data feed.
    """

    def __init__(self, host, port):
        """
        Class constructor.

        :param host: babeld local socket host
        :param port: babeld local socket port
        """

        self.host = host
        self.port = port
        self._data = None

    def _get_data(self):
        if self._data is not None:
            return self._data

        # Read the data from the remote Babel daemon.
        try:
            connection = telnetlib.Telnet(self.host, self.port)
            raw = connection.read_until('\ndone\n', 15)
            connection.close()
        except (socket.error, EOFError):
            raise BabelParseFailed

        # Parse data.
        data = {
            'node_info': {},
            'neighbours': [],
            'exported_routes': [],
            'routes': radix.Radix(),
        }

        for line in raw.split('\n'):
            try:
                command, update_type, identifier, raw_arguments = line.split(' ', 3)
                raw_arguments = raw_arguments.split(' ')
            except ValueError:
                continue

            if command != 'add':
                continue

            arguments = {}
            while raw_arguments:
                key, value = raw_arguments.pop(0), raw_arguments.pop(0)
                arguments[key] = value

            if update_type == 'self':
                # Node itself.
                data['node_info'] = {
                    'hostname': identifier,
                    'router_id': arguments['id'],
                }
            elif update_type == 'neighbour':
                # Neighbour nodes.
                data['neighbours'].append(arguments)
            elif update_type == 'xroute':
                # Exported routes.
                data['exported_routes'].append(arguments)
            elif update_type == 'route':
                # Imported routes.
                node = data['routes'].add(arguments['prefix'])
                node.data.update(arguments)

        if not data['node_info']:
            raise BabelParseFailed

        self._data = data
        return self._data

    @property
    def node_info(self):
        """
        Returns information about the local babeld node.
        """

        return self._get_data()['node_info']

    @property
    def neighbours(self):
        """
        Returns a list of neighbours.
        """

        return self._get_data()['neighbours']

    @property
    def exported_routes(self):
        """
        Returns a list of exported routes.
        """

        return self._get_data()['exported_routes']

    @property
    def routes(self):
        """
        Returns a radix tree containing all the imported routes.
        """

        return self._get_data()['routes']
