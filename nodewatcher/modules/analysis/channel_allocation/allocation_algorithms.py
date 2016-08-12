import networkx as nx

from nodewatcher.modules.analysis.channel_allocation import signal_processing
from nodewatcher.modules.analysis.channel_allocation import channel_lookup


def meta_algorithm(graph, known_nodes):
    """
    Ensures that specific algorithms are called with appropriate data structures and chooses the algorithm.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :param known_nodes: An array of BSSIDs monitored by nodewatcher.
    :return: A dictionary with two k-v pairs, one for each frequency spectrum. Keys are "2.4GHz" and "5GHz".
    """

    highest_2ghz_channel = 11

    nx_2ghz_graph = nx.Graph()
    nx_5ghz_graph = nx.Graph()
    channels_2ghz = {}
    channels_5ghz = {}

    for node in graph['v']:
        if 'b' in node:
            for bssid in node['b']:
                if channel_lookup.is_2ghz_bssid(bssid):
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
        if edge['c'] <= highest_2ghz_channel:
            chosen_graph = nx_2ghz_graph
            chosen_channels = channels_2ghz
        else:
            chosen_graph = nx_5ghz_graph
            chosen_channels = channels_5ghz

        chosen_graph.add_node(edge['t'])
        chosen_graph.add_edge(
            edge['f'],
            edge['t'],
            s=edge['s'],
            c=edge['c'],
            n=edge['n'],
        )
        if edge['t'] not in known_nodes:
            chosen_channels[edge['t']] = edge['c']

    optimal_2ghz_graph = greedy_color_with_constraints(nx_2ghz_graph, channels_2ghz)
    optimal_5ghz_graph = greedy_color_with_constraints(nx_5ghz_graph, channels_5ghz)

    channel_allocations = {}

    for node in optimal_2ghz_graph:
        channel_allocations[node] = [optimal_2ghz_graph[node]]

    for node in optimal_5ghz_graph:
        channel_allocations[node] = [optimal_5ghz_graph[node]]

    return channel_allocations


def strategy_largest_first(nx_graph):
    """
    Returns a list of the nodes of ``nx_graph`` in decreasing order by
    degree.

    :param nx_graph: NX Graph.
    :return: List of nodes in nx_graph in decreasing order by degree.
    """

    return sorted(nx_graph, key=nx_graph.degree, reverse=True)


def greedy_color_with_constraints(nx_graph, channels={}):
    """
    Custom implementation of the NetworkX function greedy_color that allows existing channel constraints.

    :param nx_graph: NX graph.
    :param channels:  existing channel constraints.
    :return: A dictionary of all nodes that were assigned a channel.
    """
    channel_dictionary = {}
    if len(nx_graph) == 0:
        return {}

    nodes = strategy_largest_first(nx_graph)
    for node in nodes:
        if node not in channels:
            # Set to keep track of channels of neighbours
            neighbour_channels = sort_neighbor_channels(nx_graph, node)

            # Find the first unused channel.
            available_channels = channel_lookup.get_available_channels(node)
            if len(neighbour_channels) < len(available_channels):
                current_channel = channel_lookup.get_channel(node)
                if current_channel not in neighbour_channels:
                    channel = current_channel
                else:
                    for channel in available_channels:
                        if channel not in neighbour_channels:
                            break
            else:
                channel = neighbour_channels[-1]

            # Add the channel to the internal tracking dictionary.
            channels[node] = channel
            for neighbor in nx_graph[node]:
                nx_graph[node][neighbor]['c'] = channel
            # Assign the new channel to the current node.
            channel_dictionary[node] = channel

    return channel_dictionary


def sort_neighbor_channels(nx_graph, node):
    """
    Sorts neighboring channels in decreasing order of signal strength. Channel spill-over is calculated according to a
    linear function. 100% of signal spills over to the same channel, 66% spill over to the next channel, 33% spills over
    two channels and nothing spills further.

    :param nx_graph: NX graph.
    :param node: Node whose neighbors need to be sorted.
    :return: Sorted list of channels of node's neighbors, sorted according to signal strength.
    """
    neighbor_channels = {}
    for neighbor in nx_graph[node]:
        new_interference = interference(nx_graph[node][neighbor]['c'], nx_graph[node][neighbor]['s'])
        for channel in new_interference:
            if channel not in neighbor_channels:
                neighbor_channels[channel] = new_interference[channel]
            else:
                neighbor_channels[channel] = signal_processing.combine_power(
                    neighbor_channels[channel],
                    new_interference[channel]
                )

    sorted_channels = sorted(neighbor_channels.items(), key=lambda x: x[1])
    return [channel[0] for channel in sorted_channels]


def interference(channel, signal):
    """
    Calculates interference on neighboring channels.

    :param channel: WiFi channel.
    :param signal: Signal strength in dB.
    :return: Dictionary of channels with non-zero interference as keys and values representing the interference in dB.
    """
    # TODO: Turn hard-coded array into a node-specific (stemming from regulatory practices) property.
    ch_2ghz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ch_5ghz = [36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 100, 102, 104, 106, 108, 110, 112, 114, 116,
               118, 120, 122, 124, 126, 128, 132, 134, 136, 138, 140, 142, 144, 149, 151, 153, 155, 157, 159, 161, 165]

    total_interference = {}
    for ch in range(channel-2, channel+3):
        if ch in ch_2ghz or ch in ch_5ghz:
            total_interference[ch] = signal_processing.amplify_interference(signal, 1 - abs(ch-channel) * 0.33)
    return total_interference
