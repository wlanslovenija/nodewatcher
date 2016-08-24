import networkx as nx

from . import channel_lookup, signal_processing


def meta_algorithm(graph, known_nodes):
    """
    Ensures that specific algorithms are called with appropriate data structures and chooses the algorithm.

    :param graph: A graph datastructure which contains both friendly and unknown nodes.
    :param known_nodes: An array of BSSIDs monitored by nodewatcher.
    :return: A dictionary with two k-v pairs, one for each frequency spectrum. Keys are "2.4GHz" and "5GHz".
    """

    # TODO: Remove hard-coded channel list.
    ch_2ghz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    highest_2ghz_channel = max(ch_2ghz)

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
        # TODO: read channel width from survey data.
        edge['w'] = 20
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
            c=channel_to_frequency(edge['c']),
            n=edge['n'],
            w=edge['w'],
        )
        if edge['t'] not in known_nodes:
            chosen_channels[edge['t']] = {
                'freq': channel_to_frequency(edge['c']),
                'width': edge['w'],
            }

    # Run the algorithm on an appropriate graph.
    optimal_2ghz_graph = greedy_color_with_constraints(nx_2ghz_graph, channels_2ghz)
    optimal_5ghz_graph = greedy_color_with_constraints(nx_5ghz_graph, channels_5ghz)
    channel_allocations = {}

    # Combine results.
    for node in optimal_2ghz_graph:
        channel_allocations[node] = {
            'freq': optimal_2ghz_graph[node]['freq'],
            'width': optimal_2ghz_graph[node]['width'],
            'interference': optimal_2ghz_graph[node]['interference'],
            'current_interference': optimal_2ghz_graph[node]['current_interference'],
        }

    for node in optimal_5ghz_graph:
        channel_allocations[node] = {
            'freq': optimal_5ghz_graph[node]['freq'],
            'width': optimal_5ghz_graph[node]['width'],
            'interference': optimal_5ghz_graph[node]['interference'],
            'current_interference': optimal_5ghz_graph[node]['current_interference'],
        }

    return channel_allocations


def channel_to_frequency(channel):
    """
    Returns a start frequency associated to a particular channel.

    :param channel: Number representing the channel of a node.
    :return: Number denoting the start frequency.
    """

    ch_to_freq = {
        '1': 2412,
        '2': 2417,
        '3': 2422,
        '4': 2427,
        '5': 2432,
        '6': 2437,
        '7': 2442,
        '8': 2447,
        '9': 2452,
        '10': 2457,
        '11': 2462,
        '36': 5180,
        '38': 5190,
        '40': 5200,
        '42': 5210,
        '44': 5220,
        '46': 5230,
        '48': 5240,
        '50': 5250,
        '52': 5260,
        '54': 5270,
        '56': 5280,
        '58': 5290,
        '60': 5300,
        '62': 5310,
        '64': 5320,
        '100': 5500,
        '102': 5510,
        '104': 5520,
        '106': 5530,
        '108': 5540,
        '110': 5550,
        '112': 5560,
        '114': 5570,
        '116': 5580,
        '118': 5590,
        '120': 5600,
        '122': 5610,
        '124': 5620,
        '126': 5630,
        '128': 5640,
        '132': 5660,
        '134': 5670,
        '136': 5680,
        '138': 5690,
        '140': 5700,
        '142': 5710,
        '144': 5720,
        '149': 5745,
        '151': 5755,
        '153': 5765,
        '155': 5775,
        '157': 5785,
        '159': 5795,
        '161': 5805,
        '165': 5825
    }

    return ch_to_freq[str(channel)]


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

    Algorithm assigns a frequency band to every node that is not in the channels dictionary. The algorithm is greedy:
    It first sorts all nodes by their degree and then iteratively chooses the best frequency band for each node. After
    all nodes have been assigned a frequency band in one specific channel width, the algorithm repeats the procedure
    with wider channel widths. It expands the channel width in case that the interference in the wider band is not
    1.2 stronger than the original interference. The constants are yet to be tweaked.

    :param nx_graph: NX graph.
    :param channels:  existing channel constraints.
    :return: A dictionary of all nodes that were assigned a frequency band, along with its interference.
    """

    # TODO: Constant that needs to be tweaked.
    cutoff_factor = 1.2

    channel_dictionary = {}
    if len(nx_graph) == 0:
        return {}

    nodes = strategy_largest_first(nx_graph)
    # TODO: Do not hard-code channel widths.
    for channel_width in (20, 40, 80):
        for node in nodes:
            if node not in channels:
                best_channel, best_interference, current_interference = optimal_channel(nx_graph, node, channel_width)

                if node in channel_dictionary:
                    interference_with_smaller_width = channel_dictionary[node]['interference']
                    cutoff_interference = signal_processing.amplify_interference(
                        interference_with_smaller_width,
                        cutoff_factor
                    )
                    if best_interference > cutoff_interference:
                        # Do not assign a wider channel to this node.
                        continue
                channel_dictionary[node] = {
                    'freq': best_channel,
                    'width': channel_width,
                    'interference': best_interference,
                    'current_interference': current_interference
                }
                for neighbor in nx_graph[node]:
                    if neighbor not in channels:
                        nx_graph[node][neighbor]['c'] = best_channel
                        nx_graph[node][neighbor]['w'] = channel_width

    return channel_dictionary


def optimal_channel(nx_graph, node, channel_width=20):
    """
    Returns the optimal frequency range for a node with the specified channel width to minimize interference
    from neighboring nodes.

    The algorithm first checks if the currently assigned channel is completely noiseless. If so, the currently assigned
    channel is kept. Otherwise, we perform a linear sweep, keeping track of the smallest interference we encountered
    thus far along with the frequency range which has minimized interference. We return the optimal frequency along
    with its interference.

    In case no frequencies are available, the algorithm will return an interference value of 0, which is too high
    to ever be used.

    :param nx_graph: NX graph.
    :param node: Node in a graph for which we're optimizing the frequency selection
    :param channel_width: Channel width in MHz.
    :return: The optimal frequency and its interference in dB.
    """

    # TODO: Tweak the noise floor constant.
    noise_floor = -95

    # Set to keep track of channels of neighbours
    frequency_list = list_neighbor_channels(nx_graph, node)

    available_frequencies = channel_lookup.get_available_frequencies(node, channel_width)
    current_channel = channel_lookup.get_channel(node)
    current_frequency = channel_to_frequency(current_channel)
    current_frequency_interference = noise_floor
    frequency_range_empty = True
    best_frequency_so_far = None
    smallest_interference_so_far = 0
    for frequency_iterator in range(current_frequency, current_frequency + channel_width + 1):
        if frequency_iterator in frequency_list:
            frequency_range_empty = False
    if frequency_range_empty:
        best_frequency_so_far = current_frequency
        smallest_interference_so_far = noise_floor
    else:
        # Current channel cannot be used. Perform a linear sweep to minimize interference.
        for frequency in available_frequencies:
            current_interference = noise_floor
            for freq in range(frequency, frequency + channel_width + 1):
                if freq in frequency_list:
                    current_interference = signal_processing.combine_power(
                        frequency_list[freq],
                        current_interference
                    )
            if frequency == current_frequency:
                current_frequency_interference = current_interference
            if current_interference < smallest_interference_so_far:
                smallest_interference_so_far = current_interference
                best_frequency_so_far = frequency

    return best_frequency_so_far, smallest_interference_so_far, current_frequency_interference


def list_neighbor_channels(nx_graph, node):
    """
    Goes through all neighbors and adds their signal strength to the interference it experiences.

    :param nx_graph: NX graph.
    :param node: Node whose neighbors need to be sorted.
    :return: Sorted list of channels of node's neighbors, sorted according to signal strength.
    """

    neighbor_channels = {}
    for neighbor in nx_graph[node]:
        new_interference = interference(
            nx_graph[node][neighbor]['c'],
            nx_graph[node][neighbor]['s'],
            nx_graph[node][neighbor]['w']
        )
        for frequency in new_interference:
            if frequency not in neighbor_channels:
                neighbor_channels[frequency] = new_interference[frequency]
            else:
                neighbor_channels[frequency] = signal_processing.combine_power(
                    signal1=neighbor_channels[frequency],
                    signal2=new_interference[frequency],
                )

    return neighbor_channels


def interference(starting_frequency, signal, channel_width=20):
    """
    Adds interference to every 20MHz frequency band within its range.

    :param starting_frequency: Frequency where the band starts.
    :param signal: Signal strength in dB.
    :param channel_width: Channel width in MHz.
    :return: Dictionary of channels with non-zero interference as keys and values representing the interference in dB.
    """

    # TODO: Possibly remove assumption that every channel is at least 20MHz wide.
    if channel_width < 20:
        channel_width = 20

    # TODO: Turn hard-coded array into a node-specific (stemming from regulatory practices) property.
    freq_list = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462, 5180, 5190, 5200, 5210, 5220, 5230,
                 5240, 5250, 5260, 5270, 5280, 5290, 5300, 5310, 5320, 5500, 5510, 5520, 5530, 5540, 5550, 5560, 5570,
                 5580, 5590, 5600, 5610, 5620, 5630, 5640, 5660, 5670, 5680, 5690, 5700, 5710, 5720, 5745, 5755, 5765,
                 5775, 5785, 5795, 5805, 5825]

    total_interference = {}
    for freq in range(starting_frequency, starting_frequency + channel_width + 1):
        if freq in freq_list:
            total_interference[freq] = signal
    return total_interference
