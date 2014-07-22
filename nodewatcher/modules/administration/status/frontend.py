from nodewatcher.core.frontend import components

from nodewatcher.core.registry import exceptions


def node_status(context):
    try:
        status = context['node'].monitoring.core.status()
    except exceptions.RegistryItemNotRegistered:
        status = None

    return {
        'node_status': status
    }

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='status',
    template='nodes/snippet/status.html',
    extra_context=node_status,
))
