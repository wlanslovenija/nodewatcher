from django_datastream import datastream

from nodewatcher import celery


@celery.app.task()
def run_downsampling():
    """
    Executes the ``downsample_streams`` API method on the datastream backend
    as some backends need this to be executed periodically.
    """

    datastream.downsample_streams()


@celery.app.task(queue='monitor')
def delete_streams(tags):
    """
    Deletes datastream streams matching ``tags``.
    """

    datastream.delete_streams(tags)
