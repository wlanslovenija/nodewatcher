from django import dispatch


# Called when node is reset.
reset_node = dispatch.Signal(providing_args=['request', 'node'])

# Called when node is removed. This is just when user interface triggers removal. Use
# django.db.models.signals.post_delete on Node model if you want to hook into object removal.
remove_node = dispatch.Signal(providing_args=['request', 'node'])
