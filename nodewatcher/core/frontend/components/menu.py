from django.conf import settings
from django.utils import translation

from . import exceptions

# Exports
__all__ = [
    'Menu',
    'MenuEntry',
    'ugettext_lazy',
]

def ugettext_lazy(message):
    translated = translation.ugettext_lazy(message)
    translated.message = message
    return translated

class MenuEntry(object):
    name = None
    label = None
    url = None
    permission_check = None
    order = 0

    def __init__(self, label=None, url=None, permission_check=None, order=0):
        if isinstance(label, basestring):
            self.name = label
            self.label = label
        elif getattr(label, 'message'):
            self.name = label.message
            self.label = label
        else:
            raise exceptions.MenuEntryHasInvalidLabel("Menu entry label must be a string or translated with nodewatcher.frontend.components.ugettext_lazy")

        self.url = url
        self.permission_check = permission_check
        self.order = order

    def get_label(self):
        return self.label

    def get_url(self):
        return self.url

    def has_permission(self, request):
        return not self.permission_check or self.permission_check(request, self)

    def get_order(self):
        return self.order

known_menus = {}

class Menu(object):
    name = None
    entries = []

    def __init__(self, name):
        if not name:
            raise exceptions.MenuHasInvalidName("Menu has invalid name")

        self.name = name

        known_menus[self.name] = self

    def add(self, entry_or_iterable):
        if not hasattr(entry_or_iterable, '__iter__'):
            entry_or_iterable = [entry_or_iterable]

        for entry in entry_or_iterable:
            if not isinstance(entry, MenuEntry):
                raise exceptions.MenuHasInvalidBase("'%s' class is not a subclass of nodewatcher.core.frontend.components.MenuEntry" % entry.__name__)

            self.entries.append(entry)

        self._sort_entries()

    def get_entries(self):
        return self.entries

    def _sort_entries(self):
        order = getattr(settings, 'MENU_%s_ORDER' % self.name.upper(), [])

        def setting_label(setting):
            if isinstance(setting, basestring):
                return setting
            else:
                return setting['label']

        def setting_order(setting, order):
            if isinstance(setting, basestring):
                return {
                    'label': setting,
                    'order': order,
                }
            else:
                setting['order'] = order
                return setting

        order_dict = dict([(setting_label(setting), setting_order(setting, order)) for (order, setting) in enumerate(order)])

        # Remove hidden entries
        self.entries = [entry for entry in self.entries if not order_dict.get(entry.name, {}).get('hide', False)]

        def sort_key(entry):
            return order_dict.get(entry.name, {}).get('order', -1), entry.order, entry.name

        # Sort entries by settings, entry order, or name
        self.entries.sort(key=sort_key, reverse=True)
