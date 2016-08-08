import networkx as nx


def meta_algorithm(graph):
    """
    Ensures that specific algorithms are called with appropriate data structures and chooses the algorithm.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :return: A dictionary with two k-v pairs, one for each frequency spectrum. Keys are "2.4GHz" and "5GHz".
    """

    number_of_2ghz_channels = 3
    number_of_5ghz_channels = 8
    highest_2ghz_channel = 11

    nx_2ghz_graph = nx.Graph()
    nx_5ghz_graph = nx.Graph()
    colors_2ghz = {}
    colors_5ghz = {}

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
            chosen_colors = colors_2ghz

        elif edge['f'] in nx_5ghz_graph.nodes():
            chosen_graph = nx_5ghz_graph
            chosen_colors = colors_5ghz

        if not chosen_graph:
            raise EnvironmentError("Node {0} belongs neither to the 2GHz nor the 5GHz network.".format(edge['f']))

        chosen_graph.add_edge(
            edge['f'],
            edge['t'],
            s=edge['s'],
            c=edge['c'],
            n=edge['n'],
        )
        chosen_colors[edge['t']] = set_edge_color(edge['c'])

    color_allocations = {
        '2.4GHz': greedy_color_with_constraints(nx_2ghz_graph, number_of_2ghz_channels, colors_2ghz),
        '5GHz': greedy_color_with_constraints(nx_5ghz_graph, number_of_5ghz_channels, colors_5ghz),
    }
    return color_allocations


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


def strategy_largest_first(nx_graph):
    """
    Returns a list of the nodes of ``nx_graph`` in decreasing order by
    degree.

    :param nx_graph: NX Graph.
    :return: List of nodes in nx_graph in decreasing order by signal strength.
    """

    return sorted(nx_graph, key=nx_graph.degree, reverse=True)


def greedy_color_with_constraints(nx_graph, number_of_colors, colors={}, strategy='largest_first'):
    """
    Custom implementation of the NetworkX function greedy_color that allows existing color constraints.

    :param nx_graph: NX graph.
    :param number_of_colors: Max number of colors we can use.
    :param colors:  existing color constraints.
    :param strategy: Strategy to order nodes for the greedy search.
    :return: A dictionary of all nodes that were assigned a color.
    """
    color_dictionary = {}
    if len(nx_graph) == 0:
        return {}

    nodes = strategy_largest_first(nx_graph)
    for u in nodes:
        if colors[u]:
            # Color already assigned.
            break

        # Set to keep track of colors of neighbours
        neighbour_colors = sort_neighbor_colors(nx_graph, u)
        # Find the first unused color.
        if len(neighbour_colors) < number_of_colors:
            for color in range(number_of_colors):
                if color not in neighbour_colors:
                    break
        else:
            color = neighbour_colors[-1]

        # Add the color to the internal tracking dictionary.
        colors[u] = color
        # Assign the new color to the current node.
        color_dictionary[u] = color

    return color_dictionary


def sort_neighbor_colors(nx_graph, u):
    """
    Sorts neighboring colors in decreasing order of signal strength. If the channels of a neighbor
    and a node do not match, the signal is set to 0.

    :param nx_graph: NX graph.
    :param u: Node whose neighbors need to be sorted.
    :return: Sorted list of colors of node's neighbors, sorted according to signal strength.
    """
    neighbor_colors = []
    for neighbor in nx_graph[u]:
        if neighbor['current_channel'] == u['current_channel']:
            neighbor_colors.append((neighbor['current_channel'], nx_graph[u][neighbor]['s']))

    sorted_colors = sorted(neighbor_colors, key=lambda x: x[1])
    return [color[0] for color in sorted_colors]
