import datetime

from nodewatcher import celery

from . import models

# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.modules.monitor.unknown_nodes.tasks.cleanup'] = {
    'task': 'nodewatcher.modules.monitor.unknown_nodes.tasks.cleanup',
    'schedule': datetime.timedelta(minutes=30),
}


@celery.app.task(queue='monitor', bind=True)
def cleanup(self):
    """
    Cleanup old unknown nodes.
    """

    models.UnknownNode.objects.filter(
        last_seen__lt=datetime.datetime.now() - datetime.timedelta(minutes=30)
    ).delete()
