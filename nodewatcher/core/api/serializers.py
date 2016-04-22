import collections
import copy
import re

from django import shortcuts
from django.conf import settings, urls
from django.core import urlresolvers

from nodewatcher.utils import loader

from . import exceptions

# Exports.
__all__ = [
    'JSONLDSerializerMixin',
    'pool'
]


class JSONLDSerializerMixin(object):
    """
    Mixin, which adds JSON-LD metadata to a serializer.
    """

    def to_representation(self, instance):
        data = super(JSONLDSerializerMixin, self).to_representation(instance)

        # Fix primary key field.
        id_field = None
        if instance._meta.pk.name in data:
            id_field = instance._meta.pk.name
        elif 'id' in data:
            id_field = 'id'

        if id_field:
            del data[id_field]
            data['@id'] = str(instance.pk)

        # Include metadata.
        base_view = getattr(self.Meta, 'base_view', None)
        if base_view is not None:
            data['@context'] = {
                '@base': urlresolvers.reverse(base_view),
                # TODO: Also include @vocab.
            }

        return data


class SerializersPool(object):
    def __init__(self):
        self._serializers = collections.OrderedDict()
        self._discovered = False
        self._states = []

    def __enter__(self):
        self._states.append((copy.copy(self._serializers), self._discovered))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future calls do not
            # raise SerializerNotRegistered or SerializerAlreadyRegistered exceptions.
            self._serializers, self._discovered = state

        # Re-raise any exception.
        return False

    def discover_serializers(self):
        with self:
            if self._discovered:
                return
            self._discovered = True

            loader.load_modules('frontend')

    def register(self, serializer):
        model = serializer.Meta.model

        if model in self._serializers:
            raise exceptions.SerializerAlreadyRegistered("A serializer for model '%s' is already registered" % model.__name__)

        self._serializers[model] = serializer

    def unregister(self, model):
        if model not in self._serializers:
            raise exceptions.SerializerNotRegistered("No serializer for model '%s' is registered" % model.__name__)

        del self._serializers[model]

    def get_all_serializers(self):
        self.discover_serializers()

        return self._serializers.values()

    def get_serializer(self, model):
        self.discover_serializers()

        try:
            return self._serializers[model]
        except KeyError:
            raise exceptions.SerializerNotRegistered("No serializer for model '%s' is registered" % model.__name__)

    def has_model(self, model):
        self.discover_serializers()

        return model in self._serializers

pool = SerializersPool()
