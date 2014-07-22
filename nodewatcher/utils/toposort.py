import functools


def topological_sort(data, dependency_key='dependencies'):
    """
    Performs a topological sort.
    """

    dep_graph = {item: value[dependency_key] for item, value in data.iteritems()}

    # Ignore self dependencies
    for key, value in dep_graph.items():
        value.discard(key)

    # Find all items that don't depend on anything
    extra_items_in_deps = functools.reduce(set.union, dep_graph.itervalues()) - set(dep_graph.iterkeys())
    # Add empty dependences where needed
    dep_graph.update({item: set() for item in extra_items_in_deps})

    while True:
        ordered = {item for item, dep in dep_graph.iteritems() if not dep}
        if not ordered:
            break

        yield [data[item] for item in ordered]

        dep_graph = {
            item: (dep - ordered)
            for item, dep in dep_graph.iteritems()
            if item not in ordered
        }

    if dep_graph:
        raise ValueError("Circular dependencies exist in dependency graph!")
