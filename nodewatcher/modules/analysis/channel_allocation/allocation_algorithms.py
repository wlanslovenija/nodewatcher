import networkx as nx


def meta_algorithm(graph, friendly_nodes):
    """
    Ensures that specific algorithms are called with appropriate data structures and chooses the algorithm.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :param friendly_nodes:  An array of nodes that are monitored by nodewatcher and are considered friendly.
    :return: A function call to the best algorithm with the correct parameters.
    """

    number_of_2ghz_channels = 3
    number_of_5ghz_channels = 8
    highest_2ghz_channel = 11

    nx_2ghz_graph = nx.Graph()
    nx_5ghz_graph = nx.Graph()

    for node in graph['v']:
        if 'b' in node and node['c'] > highest_2ghz_channel:
            nx_2ghz_graph.add_node([node['i'], {'b': node['b'], 'current_channel': node['c']}])
        elif 'b' in node and node['c'] <= highest_2ghz_channel:
            nx_5ghz_graph.add_node([node['i'], {'b': node['b'], 'current_channel': node['c']}])
        else:
            nx_2ghz_graph.add_node(node['i'])
            nx_5ghz_graph.add_node(node['i'])

    for edge in graph['e']:
        chosen_graph = None
        if edge['f'] in nx_2ghz_graph.nodes():
            chosen_graph = nx_2ghz_graph

        elif edge['f'] in nx_5ghz_graph.nodes():
            chosen_graph = nx_5ghz_graph

        if not chosen_graph:
            raise EnvironmentError("Node {0} belongs neither to the 2GHz nor the 5GHz network.".format(edge['f']))

        chosen_graph.add_edge(
            edge['f'],
            edge['t'],
            s=-1 * edge['s'],
            c=edge['c'],
            n=edge['n'],
        )
        chosen_graph.node[edge['f']]['color'] = set_edge_color(edge['c'])

    color_allocations = {
        '2.4GHz': coloring_algorithm(nx_2ghz_graph, friendly_nodes),
        '5GHz': coloring_algorithm(nx_5ghz_graph, friendly_nodes),
    }
    return color_allocations


def coloring_algorithm(graph, friendly_nodes):
    """
    Uses the greedy coloring method to assign a channel to each known node to minimize interference.

    :param graph: A NX graph which contains both friendly and unknown nodes.
    :param friendly_nodes: An array of nodes that are monitored by nodewatcher and are considered friendly.
    :return: A dictionary of all known nodes with an associated channel.
    """

    return


def set_edge_color(channel):
    color = None
    if channel <= 3:
        color = 0
    elif channel <= 8:
        color = 1
    elif channel <= 11:
        color = 2
    elif channel <= 38:
        color = 0
    elif channel <= 42:
        color = 1
    elif channel <= 46:
        color = 2
    elif channel <= 50:
        color = 3
    elif channel <= 151:
        color = 4
    elif channel <= 155:
        color = 5
    elif channel <= 159:
        color = 6
    elif channel <= 163:
        color = 7
    if color is None:
        raise EnvironmentError("Invalid channel {0}".format(channel))
    return color
