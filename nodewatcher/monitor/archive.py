
class DataArchiveQuery(object):
  """
  Query for the data archive.
  """
  def __init__(self, obj_id, metric, start, stop, step):
    """
    Constructs a new data archive query.

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

class DataArchiveBackend(object):
  """
  Provides access to an archive of time-series data for monitoring
  measurements.
  """
  def insert(self, obj_id, data, category = None):
    """
    Inserts a piece of monitoring data into the data archive. You can
    use registry items directly as data items, but they should have
    a special `data_archive` attribute present in their RegistryMeta
    section that must be an iterable containing model property names to
    be included in the data archive.

    The list of model properties can also contain tuples in which case
    the first item in the tuple is the name that will be saved into the
    data archive and the second item is the name of the property that
    will be fetched to provide the value.

    Target metric names will be composed from the category name and
    the field name. For example using category `system.status` together
    with field name `uptime` will result in `system.status.uptime` as
    the metric name.

    :param obj_id: Object that the data belongs to
    :param category: Optional metric category name
    :param data: Data describing the metrics
    """
    if hasattr(obj_id, "get_object_id"):
      obj_id = obj_id.get_object_id()

    # Extract the data item
    if hasattr(data, "RegistryMeta"):
      if category is None:
        category = data.RegistryMeta.registry_id

      new_data = {}
      for field_name in data.RegistryMeta.data_archive:
        try:
          name, alias = field_name
          new_data[name] = getattr(data, alias)
        except ValueError:
          # Only a single field name
          new_data[field_name] = getattr(data, field_name)
      data = new_data
    elif isinstance(data, dict):
      pass
    else:
      raise TypeError("Data must either be a registry item or a dictionary!")

    if category is None:
      raise ValueError("No metric category name specified!")

    for metric, value in data.iteritems():
      self.insert_metric(obj_id, "%s.%s" % (category, metric), value)

  def insert_metric(self, obj_id, metric, value):
    """
    Inserts data of a single metric into the data archive. This method
    is responsible for actual insertion of data metrics into the archive.

    :param obj_id: Object that the data belongs to
    :param metric: Name of the metric to be inserted
    :param value: Metric value
    """
    pass

  def query(self, q):
    """
    Performs a query against the data warehouse and returns the
    results.

    :param q: An instance of DataArchiveQuery
    :return: A list of resulting datapoints, sorted by time
    """
    return []

class NullDataArchive(DataArchiveBackend):
  """
  A data archive that doesn't save any data and always returns no
  results to any query.
  """
  pass

