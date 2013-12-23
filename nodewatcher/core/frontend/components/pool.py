import re

from django import shortcuts
from django.conf import settings, urls
from django.utils import importlib, datastructures

from . import exceptions

VALID_NAME = re.compile('^[A-Za-z_][A-Za-z0-9_]*$')


class FrontendComponentsPool(object):
    def __init__(self):
        self._components = datastructures.SortedDict()
        self._discovered = False

    def discover_components(self):
        if self._discovered:
            return
        self._discovered = True

        for app in settings.INSTALLED_APPS:
            try:
                importlib.import_module('.frontend', app)
            except ImportError, e:
                message = str(e)
                if message != 'No module named frontend':
                    raise

    def register(self, component_or_iterable):
        from . import base

        if not hasattr(component_or_iterable, '__iter__'):
            component_or_iterable = [component_or_iterable]

        for component in component_or_iterable:
            if not issubclass(component, base.FrontendComponent):
                raise exceptions.InvalidFrontendComponent("'%s' is not a subclass of nodewatcher.core.frontend.components.FrontendComponent" % component.__name__)

            component_name = component.get_name()

            if not VALID_NAME.match(component_name):
                raise exceptions.InvalidFrontendComponent("A frontend component '%s' has invalid name" % component_name)

            if component_name in self._components:
                raise exceptions.FrontendComponentAlreadyRegistered("A frontend component with name '%s' is already registered" % component_name)

            self._components[component_name] = component

    def unregister(self, component_or_iterable):
        if not hasattr(component_or_iterable, '__iter__'):
            component_or_iterable = [component_or_iterable]

        for component in component_or_iterable:
            component_name = component.get_name()

            if component_name not in self._components:
                raise exceptions.FrontendComponentNotRegistered("No frontend component with name '%s' is registered" % component_name)

            del self._components[component_name]

    def get_all_components(self):
        self.discover_components()

        return self._components.values()

    def get_component(self, component_name):
        self.discover_components()

        try:
            return self._components[component_name]
        except KeyError:
            raise exceptions.FrontendComponentNotRegistered("No frontend component with name '%s' is registered" % component_name)

    def has_component(self, component_name):
        self.discover_components()

        return component_name in self._components

    def get_main(self):
        """
        Returns main frontend component.
        """

        if getattr(settings, 'FRONTEND_MAIN_COMPONENT', None):
            try:
                return self.get_component(getattr(settings, 'FRONTEND_MAIN_COMPONENT'))
            except exceptions.FrontendComponentNotRegistered:
                pass

        try:
            return self.get_all_components()[0]
        except IndexError:
            raise exceptions.FrontendComponentNoneRegistered("No frontend component registered")

    def get_urls(self):
        """
        Returns Django URL patterns for all frontend components.
        """

        patterns = []
        main = self.get_main()
        main_url = main.get_main_url()

        patterns += [urls.url(r'^$', main_url['view'], kwargs=main_url.get('kwargs', None), name='main_page')]

        for component in self.get_all_components():
            component_urls = []

            try:
                component_main_url = component.get_main_url()
                component_main_regex = r'^$' if component is main else component_main_url['regex']
                component_urls += [urls.url(component_main_regex, component_main_url['view'], kwargs=component_main_url.get('kwargs', None), name=component_main_url.get('name', None))]

                if component is main:
                    # Add redirect from specified regex to main page
                    component_urls += [urls.url(component_main_url['regex'], lambda request: shortcuts.redirect('main_page', **component_main_url.get('kwargs', {})))]

            except exceptions.FrontendComponentWithoutMain:
                pass

            component_urls += component.get_urls()

            patterns += urls.url(r'^', urls.include(component_urls, namespace=component.get_name(), app_name=component.get_name())),

        return patterns

pool = FrontendComponentsPool()
