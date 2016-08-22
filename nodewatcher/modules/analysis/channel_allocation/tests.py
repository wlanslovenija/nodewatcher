import io
import json
import os
import unittest

from django import test as django_test

from . import allocation_algorithms


class ChannelAllocationTestCase(django_test.TestCase):
    fixtures = ['cloyne_wifi_monitor_fixtures']

    def __init__(self, method_name, test_filename):
        self.test_filename = test_filename
        super(ChannelAllocationTestCase, self).__init__(method_name)

    def __hash__(self):
        return hash((type(self), self._testMethodName, self.test_filename))

    def run_test(self):
        # Run the algorithm on the file and store the results.
        with io.open(self.test_filename, encoding='utf-8') as input_graph_file:
            input_graph = json.load(input_graph_file)

        algorithm_output = allocation_algorithms.meta_algorithm(
            graph=input_graph['graph'],
            known_nodes=input_graph['known_nodes'],
        )

        # Append "-results" to the end of the filename.
        results_filename = '{0}-results.json'.format(os.path.splitext(self.test_filename)[0])
        with io.open(results_filename, encoding='utf-8') as asserted_output_file:
            asserted_output = json.load(asserted_output_file)

        self.assertEqual(algorithm_output, asserted_output)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    for path, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'test_json_files')):
        for filename in files:
            # Test every JSON file that does not contain "results" in the filename.
            if os.path.splitext(filename)[1] == '.json' and 'results' not in filename:
                test_cases.addTest(ChannelAllocationTestCase('run_test', os.path.join(path, filename)))
    return test_cases
