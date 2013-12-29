from django import test as django_test
from django.conf import settings
from django.core import management
from django.db import models as django_models
from django.test import utils

from .registry_tests import models

from nodewatcher.core.registry import registration

CUSTOM_SETTINGS = {
    'INSTALLED_APPS': settings.INSTALLED_APPS + ('nodewatcher.core.registry.tests.registry_tests',),
}


@utils.override_settings(**CUSTOM_SETTINGS)
class RegistryTestCase(django_test.TestCase):
    @classmethod
    def tearDownClass(cls):
        registration.remove_point('thing.first')
        #registration.remove_point('thing.second')

    def setUp(self):
        django_models.loading.cache.loaded = False
        management.call_command('syncdb', verbosity=0, interactive=False, load_initial_data=False)

    def tearDown(self):
        # TODO: Reset
        pass

    def test_basic(self):
        # Create some things and some registry items for each thing
        for i in xrange(100):
            thing = models.Thing(foo='hello', bar=i)
            thing.save()

            simple = thing.first.foo.simple(create=models.DoubleChildRegistryItem)
            simple.interesting = 'bla'
            simple.additional = 42
            simple.another = 69
            simple.save()

        # Test basic queries
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#additional'):
            self.assertEquals(thing.f1, 42)
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#another'):
            self.assertEquals(thing.f1, 69)

        # Test foreign key traversal
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#related.name'):
            self.assertEquals(thing.f1, None)

        related = models.RelatedModel(name='test')
        related.save()
        models.DoubleChildRegistryItem.objects.update(related=related)

        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#related.name'):
            self.assertEquals(thing.f1, 'test')
