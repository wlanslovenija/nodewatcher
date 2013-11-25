from django.core import exceptions

from django_datastream import datastream


class Field(object):
    """
    A datastream Field contains metadata on how to extract datapoints and create
    streams from them. Values are then appended to these streams via the datastream
    API.
    """

    def __init__(self, attribute=None):
        """
        Class constructor.

        :param attribute: Optional name of the attribute that is source of data for
          this field
        """

        self.name = None
        self.attribute = attribute

    def prepare_value(self, value):
        """
        Performs value pre-processing before inserting it into the datastream.

        :param value: Raw value extracted from the datastream object
        :return: Processed value
        """

        return value

    def prepare_tags(self):
        """
        Returns a list of tags that will be included in the final stream.
        """

        return [{'name': self.name}]

    def prepare_query_tags(self):
        """
        Returns a list of tags that will be used to uniquely identify the final
        stream in addition to document-specific tags. This is usually a subset
        of tags returned by `prepare_tags`.
        """

        return [{'name': self.name}]

    def get_downsamplers(self):
        """
        Returns a list of downsamplers that will be used for the underlying stream.
        """

        return [
            'mean',
            'sum',
            'min',
            'max',
            'sum_squares',
            'std_dev',
            'count'
        ]

    def ensure_stream(self, obj, attributes, stream):
        """
        Creates stream and returns its identifier.

        :param obj: Source object
        :param attributes: Source object attributes
        :param stream: Stream API instance
        :return: Stream identifier
        """

        query_tags = attributes.get_stream_query_tags() + self.prepare_query_tags()
        tags = attributes.get_stream_tags() + self.prepare_tags()
        downsamplers = self.get_downsamplers()

        if hasattr(attributes, 'get_stream_highest_granularity'):
            highest_granularity = attributes.get_stream_highest_granularity()
        else:
            highest_granularity = datastream.Granularity.Seconds

        return stream.ensure_stream(query_tags, tags, downsamplers, highest_granularity)

    def to_stream(self, obj, attributes, stream):
        """
        Creates streams and inserts datapoints to the stream via the datastream API.

        :param obj: Source object
        :param attributes: Source object attributes
        :param stream: Stream API instance
        """

        attribute = self.name if self.attribute is None else self.attribute
        value = getattr(obj, attribute)
        if value is None:
            return
        
        value = self.prepare_value(getattr(obj, attribute))
        stream.append(self.ensure_stream(obj, attributes, stream), value)


class IntegerField(Field):
    """
    An integer-typed datastream field.
    """

    def __init__(self, **kwargs):
        """
        Class constructor.
        """

        super(IntegerField, self).__init__(**kwargs)

    def prepare_value(self, value):
        return int(value)

    def prepare_tags(self):
        return [{'type': 'integer'}]


class FloatField(Field):
    """
    A float-typed datastream field.
    """

    def __init__(self, **kwargs):
        """
        Class constructor.
        """

        super(FloatField, self).__init__(**kwargs)

    def prepare_value(self, value):
        return float(value)

    def prepare_tags(self):
        return [{'type': 'float'}]


class DerivedField(Field):
    """
    A derived datastream field.
    """

    def __init__(self, streams, op, **arguments):
        """
        Class constructor.

        :param streams: A list of input stream descriptors
        :param op: Operator name
        :param **arguments: Optional operator arguments
        """

        self.streams = streams
        self.op = op
        self.op_arguments = arguments

    def ensure_stream(self, obj, attributes, stream):
        """
        Creates stream and returns its identifier.

        :param obj: Source object
        :param attributes: Source object attributes
        :param stream: Stream API instance
        :return: Stream identifier
        """

        # Acquire references to input streams
        root = obj.root
        streams = []
        for field_ref in self.streams:
            path, field = field_ref['field'].split('#')
            mdl = obj
            if path:
                mdl = root.monitoring.by_path(path)

            if not hasattr(mdl, "connect_datastream"):
                raise exceptions.ImproperlyConfigured("Datastream field '%s' not found!" % field_ref['field'])

            field = mdl.connect_datastream.get_field(mdl.__class__, field)
            if field is None:
                raise exceptions.ImproperlyConfigured("Datastream field '%s' not found!" % field_ref['field'])

            mdl_attributes = mdl.connect_datastream.get_attributes(mdl)
            streams.append(
                {'name': field_ref['name'], 'stream': field.ensure_stream(mdl, mdl_attributes, stream)}
            )

        query_tags = attributes.get_stream_query_tags() + self.prepare_query_tags()
        tags = attributes.get_stream_tags() + self.prepare_tags()
        downsamplers = self.get_downsamplers()

        if hasattr(attributes, 'get_stream_highest_granularity'):
            highest_granularity = attributes.get_stream_highest_granularity()
        else:
            highest_granularity = datastream.Granularity.Seconds

        return stream.ensure_stream(
            query_tags,
            tags,
            downsamplers,
            highest_granularity,
            derive_from=streams,
            derive_op=self.op,
            derive_args=self.op_arguments,
        )

    def to_stream(self, obj, attributes, stream):
        """
        Creates streams and inserts datapoints to the stream via the datastream API.

        :param obj: Source object
        :param attributes: Source object attributes
        :param stream: Stream API instance
        """

        self.ensure_stream(obj, attributes, stream)


class ResetField(DerivedField):
    """
    A field that generates a reset stream.
    """

    def __init__(self, field):
        """
        Class constructor.
        """

        super(ResetField, self).__init__(
            [{'name': 'reset', 'field': field}],
            'counter_reset',
        )


class RateField(DerivedField):
    """
    A rate datastream field.
    """

    def __init__(self, reset_field, data_field, max_value=None):
        """
        Class constructor.
        """

        super(RateField, self).__init__(
            [
                {'name': 'reset', 'field': reset_field},
                {'name': None, 'field': data_field},
            ],
            'counter_derivative',
            max_value=max_value
        )
