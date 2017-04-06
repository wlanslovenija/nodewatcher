from django.core.management.base import BaseCommand

from ... import worker


class Command(BaseCommand):
    help = "Runs the nodewatcher monitoring daemon."
    requires_system_checks = True

    def add_arguments(self, parser):
        """Command arguments."""
        parser.add_argument('--run', type=str, help="Only execute a specific run")
        parser.add_argument('--cycles', type=int, help="Only perform a limited number of monitoring cycles")
        parser.add_argument('--process-only-node', type=str, help="Only process a specific node")

    def handle(self, *args, **options):
        w = worker.Worker()
        w.run(
            cycles=options.get('cycles', None),
            process_only_node=options.get('process_only_node', None),
            filter_run=options.get('run', None)
        )
