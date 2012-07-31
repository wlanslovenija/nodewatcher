import mongoengine

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Setup the database connection to MongoDB
# TODO Add support for specifying host, username and password
if "database" not in settings.DATA_STREAM_BACKEND_CONFIGURATION:
  raise ImproperlyConfigured("MongoDB datastream backend requires configuration!")

mongoengine.connect(settings.DATA_STREAM_BACKEND_CONFIGURATION["database"], alias = "datastream")

class MetricMap(mongoengine.Document):
  id = mongoengine.SequenceField(primary_key = True)
  tags = mongoengine.ListField(mongoengine.DictField())

  meta = dict(
    db_alias = "datastream",
    collection = "metrics",
    indexes = ["tags"]
  )

class Backend(object):
  def insert(self, metric_uri, tags, value):
    """
    Inserts a data point into the timestamped data stream.

    :param metric_uri: Unique metric identifier
    :param tags: Metric tags
    :param value: Metric value
    """
    pass

  def get_data(self, metric_uri, granularity, start, end):
    """
    Performs a query against the data stream and returns the
    results.

    :param metric_uri: Unique metric identifier
    :param granularity: Wanted data granularity
    :param start: Start timestamp
    :param end: End timestamp
    :return: A list of resulting datapoints, sorted by time
    """
    return []

  def get_metrics(self, tags):
    """
    Returns the metrics that match the specified tags.

    :param tags: A dictionary of tags to match
    :return: A list of metrics
    """
    return []
