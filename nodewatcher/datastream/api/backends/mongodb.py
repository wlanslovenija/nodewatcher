import mongoengine

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .. import errors as stream_errors

# Setup the database connection to MongoDB
# TODO Add support for specifying host, username and password
if "database" not in settings.DATA_STREAM_BACKEND_CONFIGURATION:
  raise ImproperlyConfigured("MongoDB datastream backend requires configuration!")

mongoengine.connect(settings.DATA_STREAM_BACKEND_CONFIGURATION["database"], alias = "datastream")

# TODO Should this be moved somewhere elese?
GRANULARITIES = [
  "seconds",
  "minutes",
  "hours",
  "days"
]

DOWNSAMPLERS = [
  "mean",
  "sum",
  "min",
  "max",
  "sum_squares",
  "std_dev",
  "count"
]

RESERVED_TAGS = [
  "metric_id",
  "downsamplers",
  "highest_granularity"
]

class Metric(mongoengine.Document):
  id = mongoengine.SequenceField(primary_key = True, db_alias = "datastream")
  downsamplers = mongoengine.ListField(mongoengine.StringField(choices = DOWNSAMPLERS))
  highest_granularity = mongoengine.StringField(choices = GRANULARITIES)
  tags = mongoengine.ListField(mongoengine.DynamicField())

  meta = dict(
    db_alias = "datastream",
    collection = "metrics",
    indexes = ["tags"],
    allow_inheritance = False
  )

class hashabledict(dict):
  def __key(self):
    return tuple((k,self[k]) for k in sorted(self))
  def __hash__(self):
    return hash(self.__key())
  def __eq__(self, other):
    return self.__key() == other.__key()

class Backend(object):
  def _process_tags(self, tags):
    """
    Checks that reserved tags are not used and converts dicts to their
    hashable counterparts, so they can be used in set operations.
    """
    converted_tags = set()

    for tag in tags:
      if isinstance(tag, dict):
        for reserved in RESERVED_TAGS:
          if reserved in tag:
            raise stream_errors.ReservedTagNameError

        # Convert dicts to hashable dicts so they can be used in set
        # operations
        tag = hashabledict(tag)

      converted_tags.add(tag)

    return converted_tags

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
    try:
      metric = Metric.objects.get(tags__all = query_tags)
    except Metric.DoesNotExist:
      # Create a new metric
      # TODO This is a possible race condition since MongoDB doesn't have transactions
      metric = Metric()
      metric.downsamplers = downsamplers
      metric.highest_granularity = highest_granularity
      metric.tags = list(self._process_tags(query_tags).union(self._process_tags(tags)))
      metric.save()
    except mongoengine.ValidationError:
      raise stream_errors.UnsupportedDownsampler
    except Metric.MultipleObjectsReturned:
      raise stream_errors.MultipleMetricsReturned

    return metric.id

  def get_tags(self, metric_id):
    """
    Returns the tags for the specified metric.

    :param metric_id: Metric identifier
    :return: A list of tags for the metric
    """
    try:
      metric = Metric.objects.get(id = metric_id)
      tags = metric.tags
      tags += [
        { "metric_id" : metric.id },
        { "downsamplers" : metric.downsamplers },
        { "highest_granularity" : metric.highest_granularity }
      ]
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    return tags

  def update_tags(self, metric_id, tags):
    """
    Updates metric tags with new tags, overriding existing ones.

    :param metric_id: Metric identifier
    :param tags: A list of new tags
    """
    Metric.objects(id = metric_id).update(tags = list(self._process_tags(tags)))

  def insert(self, metric_id, value):
    """
    Inserts a data point into the data stream.

    :param metric_id: Metric identifier
    :param value: Metric value
    """
    try:
      metric = Metric.objects.get(id = metric_id)
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound
    # TODO
