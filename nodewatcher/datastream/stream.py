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

  def insert(self, obj_id, metric, value):
    """
    Inserts a data point into the timestamped data stream.

    :param obj_id: Object identifier
    :param metric: Name of the metric
    :param value: Metric value
    """
    if not self.backend:
      return

    if hasattr(obj_id, "get_object_id"):
      obj_id = obj_id.get_object_id()

    return self.backend.insert(obj_id, metric, value)

  def query(self, q):
    """
    Performs a query against the data stream and returns the
    results.

    :param q: An instance of DataStreamQuery
    :return: A list of resulting datapoints, sorted by time
    """
    if not self.backend:
      return []

    return self.backend.query(q)

stream = DataStream()
