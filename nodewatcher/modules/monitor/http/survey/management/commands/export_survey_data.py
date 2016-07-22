import io
import datetime
import json

from django.core.management import base
from django.core.serializers import json as django_json

from nodewatcher.utils import trimming

from django_datastream import datastream


class Command(base.BaseCommand):
    help = trimming.trim("""
        Consolidates the survey data at the specified time from all
        nodes and exports the resulting graph as a JSON.
    """)

    def add_arguments(self, parser):
        # Optional arguments.
        parser.add_argument(
            '--at',
            type=str,
            action='store',
            dest='at_string',
            help=trimming.trim("""
                Specifies the time for which to export the survey data.
                Only the latest datapoint for each node between the specified
                time and two hours preceding the time will be used.
                Time format is 'yyyy-mm-ddThh:mm:ss' (i.e. '2007-04-10T12:00:00').
                Time has to be provided in the UTC timezone.
                By default the current time.
            """),
        )

        parser.add_argument(
            '-o',
            '--output',
            type=str,
            action='store',
            dest='output',
            help=trimming.trim("""
                If provided, the JSON output will be written to the provided
                output filename. Otherwise, the output goes to stdout.
            """),
        )

    def handle(self, *args, **options):
        """
        Exports the survey data graph as a JSON file.
        """

        at_string = options['at_string']
        output = options['output']

        if not at_string:
            at = datetime.datetime.utcnow()
        else:
            try:
                at = datetime.datetime.strptime(at_string, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise base.CommandError("Unable to parse the 'at' argument.")

        graph = all_nodes_survey_graph(at)

        if output:
            with io.open(output, 'w', encoding='utf-8') as f:
                json.dump(graph, f, ensure_ascii=False, cls=django_json.DjangoJSONEncoder)
        else:
            self.stdout.ending = None
            json.dump(graph, self.stdout, ensure_ascii=False, cls=django_json.DjangoJSONEncoder)

        if options['verbosity'] >= 2:
            self.stderr.write(self.style.SUCCESS("Successfully exported survey data."))


def all_nodes_survey_graph(at):
    """
    Returns a graph of the site survey data for a specified time. Only the latest datapoint for
    each node between the specified time and two hours preceding the time will be used.

    :param at: A datetime object.
    :return: A dictionary that contains the graph under the "graph" key.
    """

    streams = datastream.find_streams({'module': 'monitor.http.survey'})

    vertices = []
    edges = []
    # List of BSSIDs of known nodes.
    known_nodes = []
    latest_datapoint_time = None

    for stream in streams:
        datapoints = datastream.get_data(
            stream_id=stream['stream_id'],
            granularity=stream['highest_granularity'],
            start=(at - datetime.timedelta(hours=2)),
            end=at,
            reverse=True,
        )
        try:
            stream_graph = datapoints[0]['v']
            for vertex in stream_graph['v']:
                vertices.append(vertex)
                if 'b' in vertex:
                    known_nodes.append(vertex['i'])
                    for bssid in vertex['b']:
                        known_nodes.append(bssid)
            for edge in stream_graph['e']:
                edges.append(edge)
            if not latest_datapoint_time or datapoints[0]['t'] > latest_datapoint_time:
                latest_datapoint_time = datapoints[0]['t']
        except IndexError:
            pass

    if not vertices or not edges:
        raise base.CommandError("Insufficient survey data in the datastream for the specified time.")

    exported_graph = {
        'graph': {
            'vertices': vertices,
            'edges': edges,
        },
        'known_nodes': known_nodes,
        'timestamp': latest_datapoint_time
    }

    return exported_graph
