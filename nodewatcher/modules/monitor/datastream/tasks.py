from celery import task

from django_datastream import datastream

@task.task()
def run_downsampling():
    """
    Executes the `downsample_streams` API method on the datastream backend
    as some backends need this to be executed periodically.
    """
    datastream.downsample_streams([])
