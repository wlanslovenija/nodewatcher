
class Backend(object):
  """
  A null backend that doesn't insert anything and returns an empty list
  to all queries.
  """
  def insert(self, obj_id, metric, value):
    """
    Inserts a data point into the timestamped data stream.

    :param obj_id: Object identifier
    :param metric: Name of the metric
    :param value: Metric value
    """
    pass

  def query(self, q):
    """
    Performs a query against the data stream and returns the
    results.

    :param q: An instance of DataStreamQuery
    :return: A list of resulting datapoints, sorted by time
    """
    return []
