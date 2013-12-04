from django.core import exceptions

from datastream import exceptions as ds_exceptions
from django_datastream import datastream

from .pool import pool

class Field(object):
    """
    A datastream Field contains metadata on how to extract datapoints and create
    streams from them. Values are then appended to these streams via the datastream
    API.
    """

    def __init__(self, attribute=None, tags=None):
        """
        Class constructor.

        :param attribute: Optional name of the attribute that is source of data for
          this field
        :param tags: Optional custom tags
        """

        self.name = None
        self.attribute = attribute
        self.custom_tags = tags or {}

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

        return [{'name': self.name}] + [{tag: value} for tag, value in self.custom_tags.items()]

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

    def ensure_stream(self, descriptor, stream):
        """
        Creates stream and returns its identifier.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        :return: Stream identifier
        """

        query_tags = descriptor.get_stream_query_tags() + self.prepare_query_tags()
        tags = descriptor.get_stream_tags() + self.prepare_tags()
        downsamplers = self.get_downsamplers()
        highest_granularity = descriptor.get_stream_highest_granularity()

        return stream.ensure_stream(query_tags, tags, downsamplers, highest_granularity)

    def to_stream(self, descriptor, stream):
        """
        Creates streams and inserts datapoints to the stream via the datastream API.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        """

        attribute = self.name if self.attribute is None else self.attribute
        value = getattr(descriptor.get_model(), attribute)
        if value is None:
            return
        
        value = self.prepare_value(value)
        stream.append(self.ensure_stream(descriptor, stream), value)

    def set_tags(self, **tags):
        """
        Sets custom tags on this field.

        :param **tags: Keyword arguments describing the tags to set
        """

        self.custom_tags.update(tags)


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

    def __init__(self, streams, op, arguments=None, **kwargs):
        """
        Class constructor.

        :param streams: A list of input stream descriptors
        :param op: Operator name
        :param arguments: Optional operator arguments
        """

        self.streams = streams
        self.op = op
        self.op_arguments = arguments or {}

        super(DerivedField, self).__init__(**kwargs)

    def ensure_stream(self, descriptor, stream):
        """
        Creates stream and returns its identifier.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        :return: Stream identifier
        """

        # Acquire references to input streams
        root = descriptor.get_model().root
        streams = []
        for field_ref in self.streams:
            path, field = field_ref['field'].split('#')
            mdl = descriptor.get_model()
            if path:
                mdl = root.monitoring.by_path(path)

            mdl_descriptor = pool.get_descriptor(mdl)
            field = mdl_descriptor.get_field(field)
            if field is None:
                raise exceptions.ImproperlyConfigured("Datastream field '%s' not found!" % field_ref['field'])

            streams.append(
                {'name': field_ref['name'], 'stream': field.ensure_stream(mdl_descriptor, stream)}
            )

        query_tags = descriptor.get_stream_query_tags() + self.prepare_query_tags()
        tags = descriptor.get_stream_tags() + self.prepare_tags()
        downsamplers = self.get_downsamplers()
        highest_granularity = descriptor.get_stream_highest_granularity()

        return stream.ensure_stream(
            query_tags,
            tags,
            downsamplers,
            highest_granularity,
            derive_from=streams,
            derive_op=self.op,
            derive_args=self.op_arguments,
        )

    def to_stream(self, descriptor, stream):
        """
        Creates streams and inserts datapoints to the stream via the datastream API.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        """

        self.ensure_stream(descriptor, stream)


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

    def __init__(self, reset_field, data_field, max_value=None, **kwargs):
        """
        Class constructor.
        """

        super(RateField, self).__init__(
            [
                {'name': 'reset', 'field': reset_field},
                {'name': None, 'field': data_field},
            ],
            'counter_derivative',
            arguments={
                'max_value': max_value,
            },
            **kwargs
        )


class DynamicSumField(Field):
    """
    A field that computes a sum of other source fields, the list of which
    can be dynamically modified. The underlying derived stream is automatically
    recreated whenever the set of source streams changes.
    """

    def __init__(self, **kwargs):
        """
        Class constructor.
        """

        self._fields = []

        super(DynamicSumField, self).__init__(**kwargs)

    def clear_source_fields(self):
        """
        Clears all the source fields.
        """

        self._fields = []

    def add_source_field(self, field, descriptor):
        """
        Adds a source field.
        """

        self._fields.append((field, descriptor))

    def ensure_stream(self, descriptor, stream):
        """
        Creates stream and returns its identifier.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        :return: Stream identifier
        """

        # Generate a list of input streams
        streams = []
        for src_field, src_descriptor in self._fields:
            streams.append(
                {'stream': src_field.ensure_stream(src_descriptor, stream)}
            )

        if not streams:
            return

        query_tags = descriptor.get_stream_query_tags() + self.prepare_query_tags()
        tags = descriptor.get_stream_tags() + self.prepare_tags()
        downsamplers = self.get_downsamplers()
        highest_granularity = descriptor.get_stream_highest_granularity()

        try:
            return stream.ensure_stream(
                query_tags,
                tags,
                downsamplers,
                highest_granularity,
                derive_from=streams,
                derive_op='sum',
                derive_args={},
            )
        except ds_exceptions.InconsistentStreamConfiguration:
            # Drop the existing stream and re-create it
            stream.remove_streams(query_tags)
            return stream.ensure_stream(
                query_tags,
                tags,
                downsamplers,
                highest_granularity,
                derive_from=streams,
                derive_op='sum',
                derive_args={},
            )

    def to_stream(self, descriptor, stream):
        """
        Creates streams and inserts datapoints to the stream via the datastream API.

        :param descriptor: Destination stream descriptor
        :param stream: Stream API instance
        """

        self.ensure_stream(descriptor, stream)
