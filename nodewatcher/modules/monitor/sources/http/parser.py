import json
import socket
import urllib


class HttpTelemetryParseFailed(Exception):
    pass


class HttpTelemetryParser(object):
    """
    A simple class for obtaining nodewatcher telemetry in HTTP format.
    """

    def __init__(self, host=None, port=None, data=None):
        """
        Class constructor.

        :param host: Target host
        :param port: Target port
        :param data: Optional raw data to parse directly
        """

        self.host = host
        self.port = port
        self.data = data

    def parse_into(self, tree=None):
        """
        Fetches and parses data from the daemon via HTTP.

        :param tree: Target dictionary where data should be parsed into
        :return: Dictionary with parsed data
        """

        try:
            return self.parse_into_v3(tree)
        except:
            # We should also try to parse the legacy (v2) format
            return self.parse_into_v2(tree)

    def fetch_data(self, url):
        """
        Fetches data from the specified URL.

        :param url: URL template
        :return: Fetched data
        """

        if self.data is not None:
            return self.data

        socket.setdefaulttimeout(15)
        return urllib.urlopen(url.format(host=self.host, port=self.port)).read()

    def parse_into_v3(self, tree=None):
        """
        Fetches and parses data from the daemon via HTTP (legacy feed).

        :param tree: Target dictionary where data should be parsed into
        :return: Dictionary with parsed data
        """

        try:
            data = json.loads(self.fetch_data("http://{host}:{port}/nodewatcher/feed"))
        except KeyboardInterrupt:
            raise
        except:
            raise HttpTelemetryParseFailed

        if tree is None:
            tree = {}

        # Set version metadata to JSON (v3) format
        tree['_meta'] = tree.__class__()
        tree['_meta']['version'] = 3

        # Convert data to nodewatcher context format
        def convert_to_context(data):
            result = tree.__class__()
            for key, value in data.iteritems():
                if isinstance(value, dict):
                    value = convert_to_context(value)

                result[key] = value

            return result

        for key, value in data.iteritems():
            key = key.split('.')
            value = convert_to_context(value)
            reduce(lambda x, y: x.setdefault(y, x.__class__()), key[:-1], tree)[key[-1]] = value

        return tree

    def parse_into_v2(self, tree=None):
        """
        Fetches and parses data from the daemon via HTTP (legacy feed).

        :param tree: Target dictionary where data should be parsed into
        :return: Dictionary with parsed data
        """

        try:
            data = self.fetch_data("http://{host}:{port}/cgi-bin/nodewatcher")
        except KeyboardInterrupt:
            raise
        except:
            raise HttpTelemetryParseFailed

        if tree is None:
            tree = {}

        # Set version metadata to legacy (v2) format
        tree['_meta'] = tree.__class__()
        tree['_meta']['version'] = 2

        for line in data.strip().split('\n'):
            # Skip all non machine-parsable comments
            line = line.strip()
            if line.startswith(';') or not line:
                continue

            # First colon splits the key and value parts
            try:
                key, value = line.split(':', 1)
                key = key.strip().split('.')
                value = value.strip()
            except ValueError:
                raise HttpTelemetryParseFailed

            reduce(lambda x, y: x.setdefault(y, x.__class__()), key[:-1], tree)[key[-1]] = value

        return tree
