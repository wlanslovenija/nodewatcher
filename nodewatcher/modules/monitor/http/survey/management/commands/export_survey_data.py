import io
import json
import datetime

from django.core.management import base

from django_datastream import datastream


class Command(base.BaseCommand):
    help = """
    Consolidates the latest survey data within the specified time interval
    from all nodes and exports the meta graph as a JSON file.
    """

    def add_arguments(self, parser):
        # Optional arguments
        parser.add_argument(
            '--at',
            type=str,
            action='store',
            dest='string_upper_datetime',
            default=datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S'),
            help="""
            The latest data used would be collected on the date provided
            and the earliest data used would be collected
            two hours preceding the date provided. Date format is
            'yyyy-mm-ddThh:mm:ss' [i.e. '2007-04-10T12:00:00']).
            """,
        )

        parser.add_argument(
            '-b',
            '--basename',
            type=str,
            action='store',
            dest='basename',
            help="""
            If provided, survey data will be written to (basename).json.
            Otherwise, survey data will be redirected to stdout.
            """,
        )

    def handle(self, *args, **options):
        """
        Exports the latest survey data graph as a JSON file into the root directory.
        """

        string_upper_datetime = options['string_upper_datetime']
        basename = options['basename']

        try:
            upper_datetime = datetime.datetime.strptime(string_upper_datetime, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise base.CommandError("Unable to parse the date parameter.")

        exported_graph = extract_survey_graph(upper_datetime)

        if not basename:
            # Redirect to stdout.
            self.stdout.write(exported_graph, ending="")
            return

        filename = '{0}.json'.format(basename)

        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(exported_graph, ensure_ascii=False))

        self.stdout.write(self.style.SUCCESS("Successfully exported survey data."))


def extract_survey_graph(upper_datetime):
    """
    Extracts a graph of the survey during a specified time period. Only the latest data
    from specified datetime and two hours preceding the datetime will be used.

    :param upper_datetime: Datetime object according to the UTC timezone.
    :return: A dictionary that contains the graph under the 'graph' key.
    """

    streams = datastream.find_streams({'module': 'monitor.http.survey'})

    # Create a meta graph consolidating date from all streams.
    meta_vertices, meta_edges = [], []
    friendly_nodes = []
    latest_data_timepoint = None

    for stream in streams:
        datapoint_iterator = datastream.get_data(
            stream_id=stream['stream_id'],
            granularity=stream['highest_granularity'],
            start=(upper_datetime - datetime.timedelta(hours=2)),
            end=upper_datetime,
            reverse=True,
        )
        try:
            stream_graph = datapoint_iterator[0]['v']
            for vertex in stream_graph['v']:
                meta_vertices.append(vertex)
                if 'b' in vertex:
                    friendly_nodes.append(vertex['i'])
                    for bssid in vertex['b']:
                        friendly_nodes.append(bssid)
            for edge in stream_graph['e']:
                meta_edges.append(edge)
            if not latest_data_timepoint or datapoint_iterator[0]['t'] > latest_data_timepoint:
                latest_data_timepoint = datapoint_iterator[0]['t']
        except IndexError:
            pass

    if not meta_vertices or not meta_edges:
        raise LookupError("Insufficient survey data in the datastream during this time period.")

    meta_graph = {
        'v': meta_vertices,
        'e': meta_edges,
    }

    exported_graph = {
        'graph': meta_graph,
        'friendly_nodes': friendly_nodes,
        'timepoint': str(latest_data_timepoint)
    }

    return exported_graph
