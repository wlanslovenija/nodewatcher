from celery.task import task as celery_task

from nodewatcher.datastream.api.stream import stream

@celery_task()
def run_downsampling():
  """
  Executes the `downsample_metrics` API method on the datastream backend
  as some backends need this to be executed periodically.
  """
  stream.downsample_metrics([])
