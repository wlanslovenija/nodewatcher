import datetime
import mongoengine
import pymongo
import pymongo.objectid
import struct
import time
import uuid

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

class DownsampleState(mongoengine.EmbeddedDocument):
  timestamp = mongoengine.DateTimeField()

  meta = dict(
    allow_inheritance = False
  )

class Metric(mongoengine.Document):
  id = mongoengine.SequenceField(primary_key = True, db_alias = "datastream")
  external_id = mongoengine.UUIDField()
  downsamplers = mongoengine.ListField(mongoengine.StringField(choices = DOWNSAMPLERS))
  downsample_state = mongoengine.MapField(mongoengine.EmbeddedDocumentField(DownsampleState))
  downsample_needed = mongoengine.BooleanField(default = False)
  highest_granularity = mongoengine.StringField(choices = GRANULARITIES)
  tags = mongoengine.ListField(mongoengine.DynamicField())

  meta = dict(
    db_alias = "datastream",
    collection = "metrics",
    indexes = ["tags", "external_id"],
    allow_inheritance = False
  )

class hashabledict(dict):
  def __key(self):
    return tuple((k,self[k]) for k in sorted(self))
  def __hash__(self):
    return hash(self.__key())
  def __eq__(self, other):
    return self.__key() == other.__key()

class Downsamplers:
  """
  A container of downsampler classes.
  """
  class Base(object):
    """
    Base class for downsamplers.
    """
    def init(self): pass
    def update(self, datum): pass
    def finish(self, output): pass

  class Count(Base):
    """
    Counts the number of datapoints.
    """
    def init(self):
      self.count = 0

    def update(self, datum):
      self.count += 1

    def finish(self, output):
      output["c"] = self.count

  class Sum(Base):
    """
    Sums the datapoint values.
    """
    def init(self):
      self.sum = 0

    def update(self, datum):
      self.sum += datum

    def finish(self, output):
      output["s"] = float(self.sum)

  class SumSquares(Base):
    """
    Sums the squared datapoint values.
    """
    def init(self):
      self.sum = 0

    def update(self, datum):
      self.sum += datum*datum

    def finish(self, output):
      output["q"] = float(self.sum)

  class Min(Base):
    """
    Stores the minimum of the datapoint values.
    """
    def init(self):
      self.min = None

    def update(self, datum):
      if self.min is None:
        self.min = datum
      else:
        self.min = min(self.min, datum)

    def finish(self, output):
      output["l"] = self.min

  class Max(Base):
    """
    Stores the maximum of the datapoint values.
    """
    def init(self):
      self.max = None

    def update(self, datum):
      if self.max is None:
        self.max = datum
      else:
        self.max = max(self.max, datum)

    def finish(self, output):
      output["u"] = self.max

  class Mean(Base):
    """
    Computes the mean from sum and count (postprocess).
    """
    dependencies = ["sum", "count"]

    def postprocess(self, values):
      values["m"] = float(values["s"]) / values["c"]

  class StdDev(Base):
    """
    Computes the standard deviation from sum, count and sum squares
    (postprocess).
    """
    dependencies = ["sum", "count", "sum_squares"]

    def postprocess(self, values):
      n = float(values["c"])
      s = float(values["s"])
      ss = float(values["q"])
      values["d"] = (n * ss - s**2) / (n * (n-1))

class Backend(object):
  def __init__(self):
    """
    Initializes the MongoDB backend.
    """
    self.downsamplers = [
      ("count",       Downsamplers.Count),
      ("sum",         Downsamplers.Sum),
      ("sum_squares", Downsamplers.SumSquares),
      ("min",         Downsamplers.Min),
      ("max",         Downsamplers.Max),
      ("mean",        Downsamplers.Mean),
      ("std_dev",     Downsamplers.StdDev),
    ]

    # Ensure indices on datapoints collections
    db = mongoengine.connection.get_db("datastream")
    for granularity in GRANULARITIES:
      collection = getattr(db.datapoints, granularity)
      collection.ensure_index([('m', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])

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
      metric = Metric()
      metric.external_id = uuid.uuid4()

      # Some downsampling functions don't need to be stored in the database but
      # can be computed on the fly from other downsampled values
      downsamplers = set(downsamplers)
      for tag, d in self.downsamplers:
        if tag in downsamplers and hasattr(d, "dependencies"):
          downsamplers.update(d.dependencies)

      # Ensure that the granularity is a valid one and raise error otherwise
      if highest_granularity not in GRANULARITIES:
        raise stream_errors.UnsupportedGranularity

      metric.downsamplers = list(downsamplers)
      metric.highest_granularity = highest_granularity
      metric.tags = list(self._process_tags(query_tags).union(self._process_tags(tags)))

      # Initialize downsample state
      if highest_granularity != GRANULARITIES[-1]:
        for granularity in GRANULARITIES[GRANULARITIES.index(highest_granularity) + 1:]:
          metric.downsample_state[granularity] = DownsampleState()

      metric.save()
    except mongoengine.ValidationError:
      raise stream_errors.UnsupportedDownsampler
    except Metric.MultipleObjectsReturned:
      raise stream_errors.MultipleMetricsReturned

    return unicode(metric.external_id)

  def _get_metric_tags(self, metric):
    """
    Returns a metric descriptor in the form of tags.
    """
    tags = metric.tags
    tags += [
        { "metric_id" : unicode(metric.external_id) },
        { "downsamplers" : metric.downsamplers },
        { "highest_granularity" : metric.highest_granularity }
    ]
    return tags

  def get_tags(self, metric_id):
    """
    Returns the tags for the specified metric.

    :param metric_id: Metric identifier
    :return: A list of tags for the metric
    """
    try:
      metric = Metric.objects.get(external_id = metric_id)
      tags = self._get_metric_tags(metric)
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    return tags

  def update_tags(self, metric_id, tags):
    """
    Updates metric tags with new tags, overriding existing ones.

    :param metric_id: Metric identifier
    :param tags: A list of new tags
    """
    Metric.objects(external_id = metric_id).update(tags = list(self._process_tags(tags)))

  def _get_metric_queryset(self, query_tags):
    """
    Returns a queryset that matches the specified metric tags.

    :param query_tags: Tags that should be matched to metrics
    :return: A filtered queryset
    """
    query_set = Metric.objects.all()
    for tag in query_tags[:]:
      if isinstance(tag, dict):
        if "metric_id" in tag:
          query_set = query_set.filter(external_id = tag["metric_id"])
          query_tags.remove(tag)

    if not query_tags:
      return query_set
    else:
      return query_set.filter(tags__all = query_tags)

  def find_metrics(self, query_tags):
    """
    Finds all metrics matching the specified query tags.

    :param query_tags: Tags that should be matched to metrics
    :return: A list of matched metric descriptors
    """
    query_set = self._get_metric_queryset(query_tags)
    return [self._get_metric_tags(m) for m in query_set]

  def insert(self, metric_id, value):
    """
    Inserts a data point into the data stream.

    :param metric_id: Metric identifier
    :param value: Metric value
    """
    try:
      metric = Metric.objects.get(external_id = metric_id)
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    # Insert the datapoint into appropriate granularity
    db = mongoengine.connection.get_db("datastream")
    collection = getattr(db.datapoints, metric.highest_granularity)
    id = collection.insert({ "m" : metric.id, "v" : value })

    # Check if we need to perform any downsampling
    if id is not None and not metric.downsample_needed:
      self._downsample_check(metric, id.generation_time)

  def get_data(self, metric_id, granularity, start, end):
    """
    Retrieves data from a certain time range and of a certain granularity.

    :param metric_id: Metric identifier
    :param granularity: Wanted granularity
    :param start: Time range start
    :param end: Time range end
    :return: A list of datapoints
    """
    try:
      metric = Metric.objects.get(external_id = metric_id)
    except Metric.DoesNotExist:
      raise stream_errors.MetricNotFound

    # Validate specified granularity
    try:
      granularity_idx = GRANULARITIES.index(granularity)
      max_granularity_idx = GRANULARITIES.index(metric.highest_granularity)
      if granularity_idx < max_granularity_idx:
        granularity = metric.highest_granularity
    except IndexError:
      raise stream_errors.UnsupportedGranularity

    # Get the datapoints
    db = mongoengine.connection.get_db("datastream")
    collection = getattr(db.datapoints, granularity)
    pts = collection.find({
      "m" : metric.id, "_id" : {
        "$gte" : pymongo.objectid.ObjectId.from_datetime(start),
        "$lte" : pymongo.objectid.ObjectId.from_datetime(end)
      }
    }).sort("_id")

    return [{ "t" : x["_id"].generation_time, "v" : x["v"] } for x in pts]

  def downsample_metrics(self, query_tags):
    """
    Requests the backend to downsample all metrics matching the specified
    query tags.

    :param query_tags: Tags that should be matched to metrics
    """
    now = datetime.datetime.utcnow()
    qs = self._get_metric_queryset(query_tags).filter(downsample_needed = True)

    for metric in qs:
      self._downsample_check(metric, now, execute = True)

  def _round_downsampled_timestamp(self, timestamp, granularity):
    """
    Rounds the timestamp to specific time boundary defined by the
    granularity.

    :param timestamp: Raw timestamp
    :param granularity: Wanted granularity
    :return: Rounded timestamp
    """
    round_map = {
      "seconds" : ["year", "month", "day", "hour", "minute", "second"],
      "minutes" : ["year", "month", "day", "hour", "minute"],
      "hours"   : ["year", "month", "day", "hour"],
      "days"    : ["year", "month", "day"]
    }

    return datetime.datetime(**dict(((atom, getattr(timestamp, atom)) for atom in round_map[granularity])))

  def _downsample_check(self, metric, datum_timestamp, execute = False):
    """
    Checks if we need to perform any metric downsampling. In case it is needed,
    we raise a flag or perform downsampling, depending on the `execute` argument.

    :param metric: Metric instance
    :param datum_timestamp: Timestamp of the newly inserted datum
    :param execute: If set to True, downsampling will be performed, otherwise
      only a flag will be raised
    """
    for granularity in GRANULARITIES[GRANULARITIES.index(metric.highest_granularity) + 1:]:
      state = metric.downsample_state.get(granularity, None)
      rounded_timestamp = self._round_downsampled_timestamp(datum_timestamp, granularity)
      if state is None or rounded_timestamp != state.timestamp:
        if not execute:
          metric.downsample_needed = True
        else:
          self._downsample(metric, granularity, rounded_timestamp)
          metric.downsample_needed = False

    metric.save()

  def _generate_timed_object_id(self, timestamp, metric_id):
    """
    Generates a unique ObjectID for a specific timestamp and metric identifier.

    :param timestamp: Desired timestamp
    :param metric_id: 8-byte packed metric identifier
    :return: A valid object identifier
    """
    oid = ""
    # 4 bytes timestamp
    oid += struct.pack(">i", int(time.mktime(timestamp.timetuple())))
    # 8 bytes of packed metric identifier
    oid += metric_id
    return pymongo.objectid.ObjectId(oid)

  def _downsample(self, metric, granularity, current_timestamp):
    """
    Performs downsampling on the given metric and granularity.

    :param metric: Metric instance
    :param granularity: Lower granularity to downsample into
    :param current_timestamp: Timestamp of the last inserted datapoint
    """
    db = mongoengine.connection.get_db("datastream")

    # Determine the interval that needs downsampling
    datapoints = getattr(db.datapoints, metric.highest_granularity)
    state = metric.downsample_state[granularity]
    if state.timestamp is not None:
      datapoints = datapoints.find({
        "m" : metric.id, "_id" : { "$gte" : pymongo.objectid.ObjectId.from_datetime(state.timestamp) }
      })
    else:
      # All datapoints should be selected as we obviously haven't done any downsampling yet
      datapoints = datapoints.find({ "m" : metric.id })

    # Initialize downsamplers
    downsamplers = []
    for tag, downsampler in self.downsamplers:
      if tag in metric.downsamplers:
        downsamplers.append(downsampler())

    # Pack metric identifier to be used for object id generation
    metric_id = struct.pack(">Q", metric.id)

    downsampled_points = getattr(db.datapoints, granularity)
    last_timestamp = None
    for datapoint in datapoints.sort("_id"):
      ts = datapoint['_id'].generation_time
      rounded_timestamp = self._round_downsampled_timestamp(ts, granularity)
      if last_timestamp is None:
        for x in downsamplers:
          x.init()
      elif last_timestamp != rounded_timestamp:
        value = {}
        for x in downsamplers:
          x.finish(value)
          x.init()

        # Insert downsampled value
        point_id = self._generate_timed_object_id(rounded_timestamp, metric_id)
        downsampled_points.update(
          { "_id" : point_id, "m" : metric.id },
          { "_id" : point_id, "m" : metric.id, "v" : value },
          upsert = True
        )

      last_timestamp = rounded_timestamp

      # Abort when we reach the current rounded timestamp as we will process all further
      # datapoints in the next downsampling run; do not call finish on downsamplers as it
      # has already been called above when some datapoints exist
      if rounded_timestamp >= current_timestamp:
        break

      # Update all downsamplers for the current datapoint
      for x in downsamplers:
        x.update(datapoint['v'])

    # At the end, update the current timestamp in downsample_state
    metric.downsample_state[granularity].timestamp = last_timestamp
