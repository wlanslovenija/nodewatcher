from nodewatcher.core.generator.cgm import dispatcher

# Called when configuring Babel interfaces.
cgm_setup_interface = dispatcher.Signal(providing_args=['manager', 'interface'])
