__all__ = (
    'FormDefaults',
)


class FormDefaults(object):
    """
    An abstract class for defining form defaults setters.
    """

    def set_defaults(self, state):
        raise NotImplementedError
