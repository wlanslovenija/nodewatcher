
class Field(object):
  def __init__(self, alias = None, tags = None, downsamplers = None):
    self.name = None
    self.alias = alias
    self.downsamplers = downsamplers
    self.tags = tags if tags is not None else {}

  def prepare_value(self, value):
    return value

  def to_stream(self, obj, stream):
    attr = self.name if self.alias is None else self.alias
    value = self.prepare_value(getattr(obj, attr))
    tags = obj.get_metric_tags() if hasattr(obj, "get_metric_tags") else {}
    tags.update(self.tags)
    uri = obj.get_metric_id(self.name)

    # TODO

class IntegerField(Field):
  def __init__(self, **kwargs):
    super(IntegerField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return int(value)

class FloatField(Field):
  def __init__(self, **kwargs):
    super(FloatField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return float(value)

class RateField(FloatField):
  def __init__(self, **kwargs):
    super(RateField, self).__init__(**kwargs)
