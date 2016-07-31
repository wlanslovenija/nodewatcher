import unittest
import json
import io
import os

from nodewatcher.modules.analysis.rogue_nodes.tasks import rogue_node_detection_algorithm


class RogueNodeTestCase(unittest.TestCase):
    def __init__(self, method_name, algorithm_output=None, asserted_output=None):
        super(RogueNodeTestCase, self).__init__(method_name)

        self.algorithm_output = algorithm_output
        self.asserted_output = asserted_output

    def run_test(self):
        self.assertEqual(self.algorithm_output, self.asserted_output)


def load_tests(loader, tests, pattern):
    test_cases = unittest.TestSuite()
    for path, dirs, files in os.walk('nodewatcher/modules/analysis/rogue_nodes/test_json_files'):
        for filename in files:
            # Test every json file that does not contain '-results' in the filename
            if filename.split('.')[-1] == 'json' and 'results' not in filename:
                # Run the algorithm on the file and store the results.
                input_graph = json.load(io.open(os.path.join(path, filename), encoding='utf-8'))
                algorithm_output = rogue_node_detection_algorithm(
                    graph=input_graph['graph'],
                    friendly_nodes=input_graph['friendly_nodes'],
                )
                # append -results to the end of the filename
                results_filename = '{0}-results.json'.format(filename[:-5])
                asserted_output = json.load(io.open(os.path.join(path, results_filename), encoding='utf-8'))
                test_cases.addTest(RogueNodeTestCase('run_test', algorithm_output, asserted_output))
    return test_cases
