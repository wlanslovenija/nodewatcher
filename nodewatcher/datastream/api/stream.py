import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class DataStream(object):
  def __init__(self):
    """
    Class constructor.
    """
    self.backend = None

    # Load the backend as specified in configuration
    if getattr(settings, "DATA_STREAM_BACKEND", None) is not None:
      try:
        module = importlib.import_module(settings.DATA_STREAM_BACKEND)
        self.backend = getattr(module, "Backend")()
      except (ImportError, AttributeError):
        raise ImproperlyConfigured("Error importing data stream backend %s!" % settings.DATA_STREAM_BACKEND)

  def ensure_metric(self, query_tags, tags, downsamplers, highest_granularity):
    """
    Ensures that a specified metric exists.

    :param query_tags: Tags which uniquely identify a metric
    :param tags: Tags that should be used (together with `query_tags`) to create a
      metric when it doesn't yet exist
    :param downsamplers: A set of names of downsampler functions for this metric
    :param highest_granularity: Predicted highest granularity of the data the metric
      will store, may be used to optimize data storage
    :return: A metric identifier
    """
    if not self.backend:
      return

    return self.backend.ensure_metric(query_tags, tags, downsamplers, highest_granularity)

  def get_tags(self, metric_id):
    """
    Returns the tags for the specified metric.

    :param metric_id: Metric identifier
    :return: A list of tags for the metric
    """
    if not self.backend:
      return []

    return self.backend.get_tags(metric_id)

  def update_tags(self, metric_id, tags):
    """
    Updates metric tags with new tags, overriding existing ones.

    :param metric_id: Metric identifier
    :param tags: A list of new tags
    """
    if not self.backend:
      return

    return self.backend.update_tags(metric_id, tags)

  def insert(self, metric_id, value):
    """
    Inserts a data point into the data stream.

    :param metric_id: Metric identifier
    :param value: Metric value
    """
    if not self.backend:
      return

    return self.backend.insert(metric_id, value)

stream = DataStream()
