from celery.task import task as celery_task

from django_datastream import datastream

@celery_task()
def run_downsampling():
    """
    Executes the `downsample_metrics` API method on the datastream backend
    as some backends need this to be executed periodically.
    """
    datastream.downsample_metrics([])
