from django.core.management.base import BaseCommand

from web.monitor import worker

class Command(BaseCommand):
  help = "Runs the nodewatcher monitoring daemon."
  requires_model_validation = True

  def handle(self, *args, **options):
    w = worker.Worker()
    w.run()

