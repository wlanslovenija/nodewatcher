from django.core.management.base import BaseCommand

from nodewatcher.datastream import tasks as datastream_tasks

class Command(BaseCommand):
  help = "Requests the datastream backend to perform downsampling."
  requires_model_validation = True

  def handle(self, *args, **options):
    datastream_tasks.run_downsampling()
