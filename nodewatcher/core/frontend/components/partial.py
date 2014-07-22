import copy
import re

from django.conf import settings
from django.template import loader

from . import exceptions

# Exports
__all__ = [
    'Partial',
    'PartialEntry',
    'partials'
]

VALID_NAME = re.compile('^[A-Za-z_][A-Za-z0-9_]*$')


class PartialEntry(object):
    def __init__(self, name, template, visible=None, weight=0, classes=None, extra_context=None):
        if not name:
            raise exceptions.InvalidPartial("A partial entry has invalid name")

        if not VALID_NAME.match(name):
            raise exceptions.InvalidPartial("A partial entry '%s' has invalid name" % name)

        self._name = name
        self._template = template
        self._visible = visible
        self._weight = weight

        if classes is None:
            classes = ()
        self._classes = ' '.join(classes)

        self._extra_context = extra_context or {}

        self._context = None

    @property
    def name(self):
        return self._name

    @property
    def weight(self):
        return self._weight

    @property
    def classes(self):
        return self._classes

    def is_visible(self, request, context):
        return not self._visible or self._visible(self, request, context)

    def add_context(self, context):
        with_context = copy.copy(self)
        with_context._context = context
        return with_context

    def render(self, context=None):
        if context is None:
            context = self._context
        return loader.render_to_string(self._template, self._extra_context, context)


class Partial(object):
    def __init__(self, name):
        if not name:
            raise exceptions.InvalidPartial("A partial has invalid name")

        if not VALID_NAME.match(name):
            raise exceptions.InvalidPartial("A partial '%s' has invalid name" % name)

        self._name = name
        self._entries = []

    def get_name(self):
        return self._name

    @property
    def name(self):
        return self.get_name()

    def add(self, entry_or_iterable):
        if not hasattr(entry_or_iterable, '__iter__'):
            entry_or_iterable = [entry_or_iterable]

        for entry in entry_or_iterable:
            if not isinstance(entry, PartialEntry):
                raise exceptions.InvalidPartialEntry("'%s' class is not an instance of nodewatcher.core.frontend.components.PartialEntry" % entry.__name__)

            self._entries.append(entry)

        self._sort_entries()

    def get_entries(self):
        return self._entries

    @property
    def entries(self):
        return self.get_entries()

    @staticmethod
    def _setting_name(setting):
        if isinstance(setting, basestring):
            return setting
        else:
            # We require name to be present
            return setting['name']

    @staticmethod
    def _setting_weight(setting, list_index):
        if isinstance(setting, basestring):
            return {
                'name': setting,
                # We use list index as a base for weight
                'weight': list_index * 10,
            }
        elif 'weight' not in setting:
            # If weight is not specified, we use list index as a base for weight
            setting['weight'] = list_index * 10
        return setting

    @staticmethod
    def _sort_key(settings_dict):
        return lambda entry: (settings_dict.get(entry.name, {}).get('weight', 0), entry.weight)

    def _sort_entries(self):
        partial_settings = getattr(settings, 'PARTIALS', {}).get(self.name, [])

        settings_dict = dict([(self._setting_name(setting), self._setting_weight(setting, list_index)) for (list_index, setting) in enumerate(partial_settings)])

        # Remove hidden entries
        self._entries = [entry for entry in self._entries if settings_dict.get(entry.name, {}).get('visible', True)]

        # Sort partial entries by settings, entry weight, or leave it in the add order (sort is stable)
        self._entries.sort(key=self._sort_key(settings_dict))


class Partials(object):
    def __init__(self):
        self._partials = {}
        self._states = []

    def __enter__(self):
        self._states.append(copy.copy(self._partials))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future
            # calls do not raise PartialNotRegistered or
            # PartialAlreadyRegistered exceptions
            self._partials = state

        # Re-raise any exception
        return False

    def register(self, partial_or_iterable):
        if not hasattr(partial_or_iterable, '__iter__'):
            partial_or_iterable = [partial_or_iterable]

        for partial in partial_or_iterable:
            if not isinstance(partial, Partial):
                raise exceptions.InvalidPartial("'%s' class is not an instance of nodewatcher.core.frontend.components.Partial" % partial.__name__)

            if not VALID_NAME.match(partial.name):
                raise exceptions.InvalidPartial("A partial '%s' has invalid name" % partial.name)

            if partial.name in self._partials:
                raise exceptions.PartialAlreadyRegistered("A partial with name '%s' is already registered" % partial.name)

            self._partials[partial.name] = partial

    def unregister(self, partial_or_iterable):
        if not hasattr(partial_or_iterable, '__iter__'):
            partial_or_iterable = [partial_or_iterable]

        for partial in partial_or_iterable:
            if partial.name not in self._partials:
                raise exceptions.PartialNotRegistered("No partial with name '%s' is registered" % partial.name)

            del self._partials[partial.name]

    def get_all_partials(self):
        return self._partials.values()

    def get_partial(self, partial_name):
        try:
            return self._partials[partial_name]
        except KeyError:
            raise exceptions.PartialNotRegistered("No partial with name '%s' is registered" % partial_name)

    def has_partial(self, partial_name):
        return partial_name in self._partials

partials = Partials()
