import math

import networkx as nx

from nodewatcher.core.monitor import models


def meta_algorithm(graph, known_nodes):
    """
    Ensures that specific algorithms are called with appropriate data structures and chooses the algorithm.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :return: A dictionary with two k-v pairs, one for each frequency spectrum. Keys are "2.4GHz" and "5GHz".
    """

    highest_2ghz_channel = 11

    nx_2ghz_graph = nx.Graph()
    nx_5ghz_graph = nx.Graph()
    colors_2ghz = {}
    colors_5ghz = {}

    for node in graph['v']:
        if 'b' in node:
            for bssid in node['b']:
                if is_2ghz_bssid(bssid):
                    nx_2ghz_graph.add_node(bssid)
                    # Relabel edges.
                    for edge in graph['e']:
                        if edge['f'] == node['i']:
                            if edge['c'] <= highest_2ghz_channel:
                                edge['f'] = bssid
                else:
                    nx_5ghz_graph.add_node(bssid)
                    # Relabel edges.
                    for edge in graph['e']:
                        if edge['f'] == node['i']:
                            if edge['c'] > highest_2ghz_channel:
                                edge['f'] = bssid

    for edge in graph['e']:
        chosen_graph = None

        if edge['c'] <= highest_2ghz_channel:
            chosen_graph = nx_2ghz_graph
            chosen_colors = colors_2ghz
        else:
            print('added an edge to 5ghz!')
            chosen_graph = nx_5ghz_graph
            chosen_colors = colors_5ghz

        chosen_graph.add_node(edge['t'])
        chosen_graph.add_edge(
            edge['f'],
            edge['t'],
            s=edge['s'],
            c=set_edge_color(edge['c']),
            n=edge['n'],
        )
        if edge['t'] not in known_nodes:
            chosen_colors[edge['t']] = set_edge_color(edge['c'])

    optimal_2ghz_graph = greedy_color_with_constraints(nx_2ghz_graph, colors_2ghz)
    optimal_5ghz_graph = greedy_color_with_constraints(nx_5ghz_graph, colors_5ghz)

    color_allocations = {}

    for node in optimal_2ghz_graph:
        if node in color_allocations:
            color_allocations[node].append(optimal_2ghz_graph[node])
        else:
            color_allocations[node] = [optimal_2ghz_graph[node]]

    for node in optimal_5ghz_graph:
        if node in color_allocations:
            color_allocations[node].append(optimal_5ghz_graph[node])
        else:
            color_allocations[node] = [optimal_5ghz_graph[node]]

    return color_allocations


def is_2ghz_bssid(node_bssid):
    """
    Is this BSSID associated to 2.4ghz or 5ghz?

    :param node_bssid:
    :return: Boolean whether the BSSID belongs to the 2.4ghz spectrum or not.
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= 11


def set_edge_color(channel):
    color = None
    if channel <= 3:
        color = 1
    elif channel <= 8:
        color = 6
    elif channel <= 11:
        color = 11
    elif channel <= 38:
        color = 36
    elif channel <= 42:
        color = 40
    elif channel <= 46:
        color = 44
    elif channel <= 50:
        color = 48
    elif channel <= 151:
        color = 149
    elif channel <= 155:
        color = 153
    elif channel <= 159:
        color = 157
    elif channel <= 163:
        color = 161
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


def greedy_color_with_constraints(nx_graph, colors={}):
    """
    Custom implementation of the NetworkX function greedy_color that allows existing color constraints.

    :param nx_graph: NX graph.
    :param available_colors: A dictionary of available colors for each node.
    :param colors:  existing color constraints.
    :param strategy: Strategy to order nodes for the greedy search.
    :return: A dictionary of all nodes that were assigned a color.
    """
    color_dictionary = {}
    if len(nx_graph) == 0:
        return {}

    nodes = strategy_largest_first(nx_graph)
    for u in nodes:
        if u not in colors:
            # Set to keep track of colors of neighbours
            neighbour_colors = sort_neighbor_colors(nx_graph, u)

            # Find the first unused color.
            available_colors = get_available_channels(u)
            if len(neighbour_colors) < len(available_colors):
                # TODO: look into the database for the current channel. If it's unused, use it. Otherwise,
                # assign optimal channel.
                current_channel = get_channel(u)
                if current_channel not in neighbour_colors:
                    color = current_channel
                else:
                    for color in available_colors:
                        if color not in neighbour_colors:
                            break
            else:
                color = neighbour_colors[-1]

            # Add the color to the internal tracking dictionary.
            colors[u] = color
            for neighbor in nx_graph[u]:
                nx_graph[u][neighbor]['c'] = color
            # Assign the new color to the current node.
            color_dictionary[u] = color

    return color_dictionary


def get_available_channels(node_bssid):
    """
    Returns an array of available channels for that node.

    :param node_bssid: BSSID of a node
    :return: Array of available channels.
    """
    highest_2ghz_channel = 11
    channels_2ghz = [1, 6, 11]
    channels_5ghz = [36, 40, 44, 48, 149, 153, 157, 161]

    if models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= highest_2ghz_channel:
        return channels_2ghz
    else:
        return channels_5ghz


def sort_neighbor_colors(nx_graph, u):
    """
    Sorts neighboring colors in decreasing order of signal strength. If the channels of a neighbor
    and a node do not match, the signal is set to 0.

    :param nx_graph: NX graph.
    :param u: Node whose neighbors need to be sorted.
    :return: Sorted list of colors of node's neighbors, sorted according to signal strength.
    """
    neighbor_colors = {}
    for neighbor in nx_graph[u]:
        if nx_graph[u][neighbor]['c'] not in neighbor_colors:
            neighbor_colors[nx_graph[u][neighbor]['c']] = nx_graph[u][neighbor]['s']
        else:
            neighbor_colors[nx_graph[u][neighbor]['c']] = combine_power(
                nx_graph[u][neighbor]['c'],
                nx_graph[u][neighbor]['s']
            )

    sorted_colors = sorted(neighbor_colors.items(), key=lambda x: x[1])
    return [color[0] for color in sorted_colors]


def get_channel(node_bssid):
    """
    Gets the current channel of the BSSID

    :param node_bssid:
    :return:
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel


def combine_power(signal1, signal2):
    """
    Calculates the combined signal (in db) from two signals. It assumes that the output power equals the sum
    of powers of signal1 and signal2.

    :param signal1: First signal strength in dB.
    :param signal2: Second signal strength in dB.
    :return: signal strength in dB.
    """

    return 10*math.log(math.pow(10, signal1/10)+math.pow(10, signal2/10), 10)
