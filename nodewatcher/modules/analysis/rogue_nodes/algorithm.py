import networkx as nx


def rogue_node_detection_algorithm(graph, friendly_nodes):
    """
    Detects rogue nodes and outputs an array of detected rogue nodes in the graph. The algorithm first creates a
    minimum spanning tree of the graph and then computes the probability of a node being rogue from
     the number of edges that node has in a MST. The algorithm takes at most O(E log(V)) time.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :param friendly_nodes: An array of nodes that are monitored by nodewatcher and are considered friendly.
    :return: An array of all unknown nodes with an associated probability of being a rogue node.
    """

    nx_graph = nx.Graph()
    nx_graph.add_nodes_from([(node['i'], {'b': node['b']}) if 'b' in node else node['i'] for node in graph['v']])
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
            ssid_set = []
            for edge in mst.edges(node_name, data=True):
                if edge[2]['n'] not in ssid_set:
                    ssid_set.append(edge[2]['n'])
            unknown_nodes.append({
                'name': node_name,
                'probability_being_rogue': node_probability,
                'ssids': ssid_set,
            })
    return unknown_nodes
