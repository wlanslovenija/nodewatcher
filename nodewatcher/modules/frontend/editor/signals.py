from django import dispatch


# Called when node is created via the user interface.
post_create_node = dispatch.Signal(providing_args=['request', 'node'])

# Called when node is reset.
pre_reset_node = dispatch.Signal(providing_args=['request', 'node'])
reset_node = dispatch.Signal(providing_args=['request', 'node'])
post_reset_node = dispatch.Signal(providing_args=['request', 'node'])

# Called when node is removed. This is just when user interface triggers removal. Use
# django.db.models.signals.post_delete on Node model if you want to hook into node removal itself.
pre_remove_node = dispatch.Signal(providing_args=['request', 'node'])
post_remove_node = dispatch.Signal(providing_args=['request', 'node'])
