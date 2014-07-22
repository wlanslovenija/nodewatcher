from django import dispatch


# Called when node is reset.
reset_node = dispatch.Signal(providing_args=['request', 'node'])

# Called when node is removed.
remove_node = dispatch.Signal(providing_args=['request', 'node'])
