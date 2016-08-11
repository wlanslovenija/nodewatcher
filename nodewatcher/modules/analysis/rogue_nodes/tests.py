import io
import json
import os
import unittest

from . import algorithm


class RogueNodeTestCase(unittest.TestCase):
    def __init__(self, method_name, test_filename):
        super(RogueNodeTestCase, self).__init__(method_name)

        self.test_filename = test_filename

    def run_test(self):
        # Run the algorithm on the file and store the results.
        with io.open(self.test_filename, encoding='utf-8') as input_graph_file:
            input_graph = json.load(input_graph_file)

        algorithm_output = algorithm.rogue_node_detection_algorithm(
            graph=input_graph['graph'],
            friendly_nodes=input_graph['friendly_nodes'],
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
                test_cases.addTest(RogueNodeTestCase('run_test', os.path.join(path, filename)))
    return test_cases
