from nodewatcher.core.frontend import components


components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='irnas_koruzav2',
    template='nodes/snippet/irnas_koruzav2.html',
    extra_context=lambda context: {
        'serial_number': getattr(context['node'].monitoring.irnas.koruza(), 'serial_number', None),
    },
))
