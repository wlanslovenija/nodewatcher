
class Field(object):
  def __init__(self, attribute = None, highest_granularity = None):
    self.name = None
    self.attribute = attribute
    self.highest_granularity = highest_granularity

  def prepare_value(self, value):
    return value

  def prepare_tags(self, value):
    return [{ "name" : self.name }]

  def prepare_query_tags(self, value):
    return [{ "name" : self.name }]

  def get_downsamplers(self):
    return [
      "mean",
      "sum",
      "min",
      "max",
      "sum_squares",
      "std_dev",
      "count"
    ]

  def to_stream(self, obj, stream):
    attribute = self.name if self.attribute is None else self.attribute
    value = self.prepare_value(getattr(obj, attribute))
    query_tags = obj.get_metric_query_tags() + self.prepare_query_tags(value)
    tags = obj.get_metric_tags() + self.prepare_tags(value)
    downsamplers = self.get_downsamplers()

    if self.highest_granularity is not None:
      highest_granularity = self.highest_granularity
    elif hasattr(obj, "get_metric_highest_granularity"):
      highest_granularity = obj.get_metric_highest_granularity()
    else:
      highest_granularity = "seconds"

    metric_id = stream.ensure_metric(query_tags, tags, downsamplers, highest_granularity)
    stream.insert(metric_id, value)

class IntegerField(Field):
  def __init__(self, **kwargs):
    super(IntegerField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return int(value)

  def prepare_tags(self, value):
    return [{ "type" : "integer" }]

class FloatField(Field):
  def __init__(self, **kwargs):
    super(FloatField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return float(value)

  def prepare_tags(self, value):
    return [{ "type" : "float" }]

class RateField(FloatField):
  def __init__(self, **kwargs):
    super(RateField, self).__init__(**kwargs)
