from optparse import make_option

from django.core.management.base import BaseCommand

from ... import worker


class Command(BaseCommand):
    help = "Runs the nodewatcher monitoring daemon."
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option('--cycles',
            dest='cycles',
            default=None,
            type=int,
            help='Only perform a limited number of monitoring cycles',
        ),
        make_option('--process-only-node',
            dest='process_only_node',
            default=None,
            help='Only process a specific node',
        ),
    )

    def handle(self, *args, **options):
        w = worker.Worker()
        w.run(cycles=options['cycles'], process_only_node=options['process_only_node'])
