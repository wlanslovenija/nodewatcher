import inspect
import random
import string

from django.apps import apps
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core import exceptions


def generate_random_password(length=8):
    """
    Generates a random password.
    """

    # Re-seed random number generator
    # This can make random values even more predictable if for seed
    # a time-dependent value is used as time of password generation
    # is easier to deduce than time of the first seed initialization
    # But Python uses os.urandom source if available so we are probably
    # better off
    random.seed()

    x = ''
    for i in xrange(0, length):
        x += random.choice(string.ascii_letters + string.digits)

    return x


def intersect(a, b):
    """
    Finds the intersection of two dictionaries.

    A key and value pair is included in the result only if the key exists in both given dictionaries. Value is taken from
    the second dictionary.
    """

    return dict(filter(lambda (x, y): x in a, b.items()))


def initial_accepts_request(request, form_class):
    """
    If fields in the given form uses dynamic initial values which accepts request argument it wraps them so that request is given
    to them when called.
    """

    initial = {}

    for name, field in form_class.base_fields.items():
        if callable(field.initial):
            try:
                if len(inspect.getargspec(field.initial)[0]) == 1:
                    # We fight Python aliasing in for loops here
                    initial[name] = (lambda fi: lambda: fi(request))(field.initial)
            except:
                pass

    if not initial:
        return form_class

    def wrapper(*args, **kwargs):
        initial.update(kwargs.get('initial', {}))
        kwargs['initial'] = initial
        return form_class(*args, **kwargs)

    return wrapper
