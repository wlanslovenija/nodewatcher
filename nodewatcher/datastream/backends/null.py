
class Backend(object):
  """
  A null backend that doesn't insert anything and returns an empty list
  to all queries.
  """
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
