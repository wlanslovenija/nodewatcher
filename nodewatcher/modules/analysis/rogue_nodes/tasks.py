import datetime

from django.core.mail import send_mail

from django.conf import settings

from nodewatcher import celery

from nodewatcher.modules.monitor.http.survey.management.commands.export_survey_data import extract_survey_graph

import networkx as nx

# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.modules.analysis.rogue_nodes.tasks.rogue_node_detection'] = {
    'task': 'nodewatcher.modules.analysis.rogue_nodes.tasks.rogue_node_detection',
    'schedule': datetime.timedelta(days=1),
}


@celery.app.task(queue='monitor', bind=True)
def rogue_node_detection(self):
    """
    Detects rogues nodes and issues a warning to its neighbors that are monitored by nodewatcher.
    """

    extracted_graph = extract_survey_graph()

    if not extracted_graph:
        return

    # Run the algorithm on the meta graph.
    unknown_node_list = rogue_node_detection_algorithm(extracted_graph['graph'], extracted_graph['friendly_nodes'])

    rogue_node_list = filter(lambda unknown_node: unknown_node['probability_being_rogue'] > 0.9, unknown_node_list)

    if rogue_node_list:
        send_mail(
            subject="Rogue nodes detected",
            message="We detected the following rogue nodes: {0}".format(rogue_node_list),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["to@example.com"],
            fail_silently=False,
        )


def rogue_node_detection_algorithm(graph, friendly_nodes):
    """
    Detects rogue nodes and outputs an array of detected rogue nodes in the graph. The algorithm first creates a
    minimum spanning tree of the graph and goes through all the nodes with at least two edges in the MST. If at least
    three edges are present, declare that node to be rogue. If two edges are present, we perform a linear time
    correction step. The algorithm takes at most O(EV log(V)) time.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :param friendly_nodes: An array of nodes that are monitored by nodewatcher and are considered friendly.
    :return: An array of all unknown nodes with an associated probability of being a rogue node.
    """

    nx_graph = nx.Graph()
    nx_graph.add_nodes_from([(node['i'], {'b': node['b']}) if 'b' in node else node['i'] for node in graph["v"]])
    nx_graph.add_edges_from([(edge['f'], edge['t'], {
        's': -1 * edge['s'],
        'c': edge['c'],
        'n': edge['n'],
    }) for edge in graph['e']])

    # Create a MST with Kruskal's
    mst = nx.minimum_spanning_tree(nx_graph, weight='s')

    unknown_nodes = []
    for node_name in mst.node:
        if node_name not in friendly_nodes:
            node_probability = min((mst.degree(node_name) - 1) / 2.0, 1)
            ssid_set = set()
            for edge in mst.edges(node_name, data=True):
                ssid_set.add(edge[2]['n'])
            unknown_nodes.append({
                'name': node_name,
                'probability_being_rogue': node_probability,
                'ssids': ssid_set,
            })

    return unknown_nodes
