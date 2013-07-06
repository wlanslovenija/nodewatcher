from . import exceptions

# Exports
__all__ = [
    'FrontendComponent',
]

class FrontendComponent(object):
    name = None
    dependencies = ()
    urls = None

    def __init__(self):
        # To prevent import cycle
        from .pool import pool

        for dependency in self.get_dependencies():
            if not pool.has_component(dependency):
                raise exceptions.FrontendComponentDependencyNotRegistered("Frontend component '%s' depends on '%s', but the latter is not registered" % (self.get_name(), dependency))

    @classmethod
    def get_name(cls):
        if cls.name:
            return cls.name

        name = cls.__name__
        if name.endswith('Component'):
            name = name[:-9]
        return name.lower()

    @classmethod
    def get_dependencies(cls):
        return cls.dependencies

    @classmethod
    def get_main_url(cls):
        """
        Returns ``{regex, view, kwargs, name}`` dict used for the main page pattern and it is
        prepended to those returned by ``get_urls``. If this component is selected for the main
        page, ``regex`` is ignored and root regex is used.
        """

        raise exceptions.FrontendComponentWithoutMain("Frontend component '%s' is without main URL pattern" % cls.get_name())

    @classmethod
    def get_urls(cls):
        return cls.urls or []
