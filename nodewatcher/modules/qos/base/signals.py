from nodewatcher.core.generator.cgm import dispatcher

# Called while processing CGMs and interface QoS should be applied.
cgm_apply_interface = dispatcher.Signal(providing_args=['qos', 'interface', 'network'])
