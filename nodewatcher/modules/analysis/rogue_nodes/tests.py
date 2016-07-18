from django import test as django_test

from nodewatcher.modules.analysis.rogue_nodes.tasks import rogue_node_detection_algorithm

import json
import io
import os


class RogueDetectionTest(django_test.TestCase):

    def test_rogue_detection_algorithm(self):
        print('testing rogue_node_detection_algorithm')
        for path, dirs, files in os.walk('nodewatcher/modules/analysis/rogue_nodes/test_json_files'):
            for filename in files:
                # Test every json file that does not contain '-results' in the filename
                if filename.split('.')[-1] == 'json' and 'results' not in filename:
                    # Run the algorithm on the file and compare the results.
                    print('testing ' + str(filename))
                    input_graph = json.load(io.open(os.path.join(path, filename), encoding='utf-8'))
                    output_results = rogue_node_detection_algorithm(
                        graph=input_graph['graph'],
                        friendly_nodes=input_graph['friendly_nodes'],
                    )
                    # append -results to the end of the filename
                    results_filename = '{0}-results.json'.format(filename[:-5])
                    asserted_results = json.load(io.open(os.path.join(path, results_filename), encoding='utf-8'))
                    assert (output_results == asserted_results)
