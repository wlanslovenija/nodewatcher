
class ConnectDatastream(object):
  def __init__(self, **kwargs):
    """
    Constructs datastream metadata descriptor. Keyword arguments should contain
    datastream field definitions.
    """
    self.fields = {}
    for name, field in kwargs.items():
      field.name = name
      self.fields[name] = field

  def insert_to_stream(self, obj, stream):
    """
    Inserts all the fields specified in this descriptor to the datastream.

    :param obj: Object instance that contains the raw data
    :param stream: Instance of the datastream to insert into
    """
    for field in self.fields.values():
      field.to_stream(obj, stream)
