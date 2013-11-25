

class ConnectDatastream(object):
    """
    Specifies datastream field metadata.
    """

    def __init__(self, attributes_class, **kwargs):
        """
        Constructs datastream metadata descriptor. Keyword arguments should contain
        datastream field definitions.
        """

        self.attributes_class = attributes_class
        self.fields = {}
        for name, field in kwargs.items():
            field.name = name
            self.fields[name] = field

    def get_attributes(self, obj):
        """
        Returns the attributes object for a specific model instance.

        :param obj: Object instance
        """

        return self.attributes_class(obj)

    def get_field(self, cls, name):
        """
        Returns the field descriptor for a specific field.

        :param cls: Model class
        :param name: Field name
        :return: Field descriptor or None
        """

        if name in self.fields:
            return self.fields[name]

        # Include all fields from parent classes
        for parent in cls.__bases__:
            if not hasattr(parent, 'connect_datastream'):
                continue

            value = parent.connect_datastream.get_field(parent, name)
            if value is not None:
                return value

    def insert_to_stream(self, cls, obj, stream):
        """
        Inserts all the fields specified in this descriptor to the datastream.

        :param cls: Model class
        :param obj: Object instance that contains the raw data
        :param stream: Instance of the datastream to insert into
        """

        attributes = self.get_attributes(obj)

        for field in self.fields.values():
            field.to_stream(obj, attributes, stream)

        # Include all fields from parent classes
        for parent in cls.__bases__:
            if not hasattr(parent, 'connect_datastream'):
                continue

            parent.connect_datastream.insert_to_stream(parent, obj, stream)
