from django.core.management import base

from ... import tasks


class Command(base.BaseCommand):
    help = "Requests the datastream backend to perform downsampling."
    requires_model_validation = True

    def handle(self, *args, **options):
        tasks.run_downsampling()
