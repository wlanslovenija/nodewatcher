import datetime

from django.utils import timezone

from nodewatcher import celery

from . import models

# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.core.generator.tasks.cleanup'] = {
    'task': 'nodewatcher.core.generator.tasks.cleanup',
    'schedule': datetime.timedelta(minutes=30),
}


@celery.app.task(queue='monitor', bind=True)
def cleanup(self):
    """
    Cleanup old build results.
    """

    models.BuildResult.objects.filter(
        last_modified__lt=timezone.now() - datetime.timedelta(days=30)
    ).delete()
