from nodewatcher.core.frontend import components


components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='irnas_koruza',
    template='nodes/snippet/irnas_koruza.html',
    extra_context=lambda context: {
        'vpn_ip': getattr(context['node'].monitoring.koruza.vpn(), 'ip_address', None),
    }
))
