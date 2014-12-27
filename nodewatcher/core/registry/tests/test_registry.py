import random

from django import test as django_test
from django.apps import apps
from django.conf import settings
from django.core import management, exceptions as django_exceptions
from django.db.models import query
from django.test import utils

from .registry_tests import models

from nodewatcher.core.registry import registration, exceptions

CUSTOM_SETTINGS = {
    'DEBUG': True,
    'INSTALLED_APPS': settings.INSTALLED_APPS + ('nodewatcher.core.registry.tests.registry_tests',),
}


@utils.override_settings(**CUSTOM_SETTINGS)
class RegistryTestCase(django_test.TransactionTestCase):
    @classmethod
    def tearDownClass(cls):
        registration.remove_point('thing.first')
        #registration.remove_point('thing.second')

    def setUp(self):
        apps.clear_cache()
        management.call_command('syncdb', verbosity=0, interactive=False, load_initial_data=False)

    def tearDown(self):
        # TODO: Reset
        pass

    def test_basic(self):
        # Create some things and some registry items for each thing
        for i in xrange(100):
            thing = models.Thing(foo='hello', bar=i)
            thing.save()

            simple = thing.first.foo.simple(default=models.DoubleChildRegistryItem)
            self.assertEquals(simple.another, 17)
            self.assertEquals(simple.pk, None)

            simple = thing.first.foo.simple(create=models.DoubleChildRegistryItem)
            self.assertNotEquals(simple.pk, None)
            simple.interesting = 'bla'
            simple.additional = 42
            simple.another = 69
            simple.level = 'level-x'
            simple.save()

            item = thing.second.foo.multiple(create=models.FirstSubRegistryItem)
            item.foo = 3
            item.bar = 88
            item.save()

            item = thing.second.foo.multiple(create=models.SecondSubRegistryItem)
            item.foo = 3
            item.moo = 77
            item.save()

            item = thing.second.foo.multiple(create=models.ThirdSubRegistryItem)
            item.foo = 3
            item.moo = 77
            item.save()

        # Test basic queries
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#additional'):
            self.assertEquals(thing.f1, 42)
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#another'):
            self.assertEquals(thing.f1, 69)

        with self.assertRaises(ValueError):
            models.Thing.objects.regpoint('first').registry_fields(f1='this.is.an.invalid.specifier###')
        with self.assertRaises(exceptions.RegistryItemNotRegistered):
            models.Thing.objects.regpoint('first').registry_fields(f1='foo.invalid#additional')

        # Test foreign key traversal
        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#related.name'):
            self.assertEquals(thing.f1, None)

        related = models.RelatedModel(name='test')
        related.save()
        models.DoubleChildRegistryItem.objects.update(related=related)

        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#related.name'):
            self.assertEquals(thing.f1, 'test')

        for thing in models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple'):
            self.assertEquals(thing._meta.virtual_fields[0].rel.to, models.SimpleRegistryItem)
            self.assertEquals(thing.f1.interesting, 'bla')
            self.assertEquals(thing.f1.additional, 42)

        for thing in models.Thing.objects.regpoint('first').registry_fields(f1=models.DoubleChildRegistryItem):
            self.assertEquals(thing._meta.virtual_fields[0].rel.to, models.DoubleChildRegistryItem)
            self.assertEquals(thing.f1.interesting, 'bla')
            self.assertEquals(thing.f1.additional, 42)

        for thing in models.Thing.objects.regpoint('first').registry_fields(f1=models.AnotherRegistryItem):
            self.assertEquals(thing.f1.interesting, 'nope')
            self.assertEquals(thing.f1.pk, None)

        with self.assertRaises(TypeError):
            models.Thing.objects.regpoint('first').registry_fields(f1=models.FirstSubRegistryItem)

        # Test filter queries
        thing = models.Thing.objects.all()[0]
        mdl = thing.first.foo.simple()
        mdl.another = 42
        mdl.save()

        items = models.Thing.objects.regpoint('first').registry_filter(foo_simple__another=69)
        self.assertEquals(len(items), 99)
        items = models.Thing.objects.regpoint('first').registry_filter(foo_simple__another=42)
        self.assertEquals(len(items), 1)

        # Test proxy field filter
        qs = models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#related.name')
        qs = qs.filter(f1__icontains='Test')
        self.assertEqual(len(qs), 100)

        qs = models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple')
        qs = qs.filter(f1__related__name__icontains='Test')
        self.assertEqual(len(qs), 100)

        # Test that fallthrough fields also work
        qs = qs.filter(id=1)
        self.assertEqual(len(qs), 1)

        # Test that passing Q objects work.
        qs = qs.filter(query.Q(id=2))
        self.assertEqual(len(qs), 0)

        # Test filter exceptions
        with self.assertRaises(django_exceptions.FieldError):
            qs = qs.filter(nonexistant='foo')

        # Test class query
        self.assertEquals(registration.point('thing.first').get_class('foo.simple', 'SimpleRegistryItem'), models.SimpleRegistryItem)
        self.assertEquals(registration.point('thing.first').get_class('foo.simple', 'ChildRegistryItem'), models.ChildRegistryItem)
        self.assertEquals(registration.point('thing.first').get_class('foo.simple', 'DoubleChildRegistryItem'), models.DoubleChildRegistryItem)
        with self.assertRaises(exceptions.UnknownRegistryClass):
            self.assertEquals(registration.point('thing.first').get_class('foo.simple', 'doesnotexist'))

        # Test polymorphic cascade deletions
        thing.delete()

    def test_choices(self):
        ordered_choices = ['level-x', 'level-a', 'level-m']
        ordered_pks = []

        for i in xrange(30):
            thing = models.Thing(foo='hello', bar=i)
            thing.save()

            related = models.RelatedModel(name='test', level=random.choice(ordered_choices))
            related.save()

            order = (ordered_choices.index(related.level), thing.id)

            simple = thing.first.foo.simple(create=models.DoubleChildRegistryItem)
            simple.interesting = '%06d-%06d' % order
            simple.additional = 42
            simple.another = 69
            simple.level = related.level
            simple.related = related
            simple.save()

            ordered_pks.append(order)

        ordered_pks = [x[1] for x in sorted(ordered_pks)]

        qs = models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple#level')

        # Ensure that field descriptors are available
        for item in qs:
            with self.assertRaises(AttributeError):
                item.get_level_choice()

            self.assertEquals(item.get_f1_choice().name, item.f1)

        # Check if ordering works properly
        ordered = [item.pk for item in qs.order_by('f1', 'id')]
        self.assertEqual(ordered, ordered_pks)

        # Test ordering by using relations.
        qs = models.Thing.objects.regpoint('first').registry_fields(f1='foo.simple')
        ordered = [item.pk for item in qs.order_by('f1__level', 'id')]
        self.assertEqual(ordered, ordered_pks)
        ordered = [item.pk for item in qs.order_by('f1__interesting', 'id')]
        self.assertEqual(ordered, ordered_pks)

        # Test ordering by registry id without fetching the field explicitly
        qs = models.Thing.objects.regpoint('first')
        ordered = [item.pk for item in qs.order_by('foo.simple#level', 'id')]
        self.assertEqual(ordered, ordered_pks)
        ordered = [item.pk for item in qs.order_by('foo.simple#related.level', 'id')]
        self.assertEqual(ordered, ordered_pks)

        # Test regpoint specifier syntax.
        qs = models.Thing.objects.all()
        ordered = [item.pk for item in qs.order_by('first:foo.simple#level', 'id')]
        self.assertEqual(ordered, ordered_pks)

    def test_prefetch_queryset(self):
        thing = models.Thing(foo='hello', bar=1)
        thing.save()

        simple = thing.first.foo.simple(create=models.SimpleRegistryItem)
        simple.interesting = 'foo'
        simple.level = 'level-x'
        simple.save()

        qs = models.Thing.objects.regpoint('first').registry_fields(
            f1=models.SimpleRegistryItem.objects.all().extra(select={'test': '42'}),
        )
        for thing in qs:
            self.assertEqual(thing.f1.interesting, 'foo')
            self.assertEqual(thing.f1.level, 'level-x')
            self.assertEqual(thing.f1.get_level_display(), 'Level 0')
            self.assertEqual(thing.f1.test, 42)

    def test_prefetch_queryset_default(self):
        thing = models.Thing(foo='hello', bar=1)
        thing.save()

        qs = models.Thing.objects.regpoint('first').registry_fields(
            f1=models.SimpleRegistryItem.objects.all().extra(select={'test': '42'}),
        )
        for thing in qs:
            self.assertEqual(thing.f1.interesting, 'nope')
            self.assertEqual(thing.f1.level, None)
            self.assertEqual(thing.f1.test, None)
