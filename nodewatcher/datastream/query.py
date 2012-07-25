
class DataStreamQuery(object):
  """
  Query for the data stream.
  """
  def __init__(self, obj_id, metric, start, stop, step):
    """
    Constructs a new data stream query.

    :param obj_id: Object that the data belongs to
    :param metric: Metric name
    :param start: Start timestamp
    :param stop: Stop timestamp
    :param step: Time step in seconds
    """
    if hasattr(obj_id, "get_object_id"):
      obj_id = obj_id.get_object_id()

    self.obj_id = obj_id
    self.metric = metric
    self.start = start
    self.stop = stop
    self.step = step
