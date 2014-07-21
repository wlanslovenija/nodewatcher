import unittest

from django.conf import settings
from django.test import testcases, runner
from django.utils import unittest as django_unittest


class FilteredTestSuiteRunner(runner.DiscoverRunner):
    """
    It is the same as in DjangoTestSuiteRunner, but it also supports filtering only
    wanted tests through ``TEST_RUNNER_FILTER`` Django setting.
    """

    def _filter_suite(self, suite):
        filters = getattr(settings, 'TEST_RUNNER_FILTER', None)

        if filters is None:
            # We do NOT filter if filters are not set
            return suite

        # Add unittest prefix to not filter special tests like unittest.loader.ModuleImportFailure
        filters += ('unittest.',)

        filtered = django_unittest.TestSuite()

        for test in suite:
            if isinstance(test, (unittest.TestSuite, django_unittest.TestSuite)):
                filtered.addTests(self._filter_suite(test))
            else:
                for f in filters:
                    if test.id().startswith(f):
                        filtered.addTest(test)

        return filtered

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = super(FilteredTestSuiteRunner, self).build_suite(test_labels, extra_tests=None, **kwargs)
        suite = self._filter_suite(suite)
        return runner.reorder_suite(suite, (testcases.TestCase,))
