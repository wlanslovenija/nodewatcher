import io
import datetime
import json

from django.core.management import base
from django.core.serializers import json as django_json

from nodewatcher.utils import trimming
from nodewatcher.modules.monitor.http.survey import extract_nodes


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

        graph = extract_nodes.all_nodes_survey_graph(at)

        # TODO: "unicode" does not exist anymore in Python 3.5.
        #       But json.dumps returns there a normal string, and not once str and once unicode like in Python 2.
        json_graph = unicode(json.dumps(
            graph,
            ensure_ascii=False,
            cls=django_json.DjangoJSONEncoder,
            sort_keys=True,
            indent=4,
            separators=(',', ': '),
        ))

        if output:
            with io.open(output, 'w', encoding='utf-8') as f:
                f.write(json_graph)
        else:
            self.stdout.write(json_graph, ending='')

        if options['verbosity'] >= 2:
            self.stderr.write(self.style.SUCCESS("Successfully exported survey data."))
