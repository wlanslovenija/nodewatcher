from django.core import validators, exceptions
from django.utils import deconstruct
from django.utils.translation import ugettext_lazy as _


class NodeNameValidator(validators.RegexValidator):
    """
    Validates a node's name.
    """

    regex = r'^[a-z](?:-?[a-z0-9]+)*$'
    message = _('Node name contains invalid characters.')


@deconstruct.deconstructible
class PortNumberValidator(object):
    """
    Validates a port number.
    """

    message = _('Port should be between 1 and 49151.')

    def __call__(self, value):
        if value < 1 or value > 49151:
            raise exceptions.ValidationError(self.message, code='invalid_port')
