__all__ = (
    'FormDefaults',
)


class FormDefaults(object):
    """
    An abstract class for defining form defaults setters.
    """

    # Set to True to ensure that these defaults are applied even when the
    # user has disabled defaults for a specific device.
    always_apply = False

    def set_defaults(self, state, create):
        raise NotImplementedError
