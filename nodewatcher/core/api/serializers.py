import collections
import copy
import re

from django import shortcuts
from django.conf import settings, urls

from nodewatcher.utils import loader

from . import exceptions


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
