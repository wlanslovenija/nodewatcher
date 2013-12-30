from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

# TODO: Descriptions should be read from the registry

NETWORK_DESCRIPTIONS = {
    'up': _("The node is reachable."),
    'down': _("The node is not connected to the network."),
    'visible': _("The node is connected to the network but a network connection to it cannot be established."),
    'unknown': _("The network status of the node is unknown."),
}

MONITORED_DESCRIPTIONS = {
    True: _("The node is monitored by <i>nodewatcher</i>."),
    False: _("The node is not monitored by <i>nodewatcher</i>."),
    None: _("The monitored status of the node is unknown."),
}

HEALTH_DESCRIPTIONS = {
    'healthy': _("No issues with the node have been detected."),
    'warnings': _("Minor issues with the node have been detected."),
    'errors': _("Serious issues with the node have been detected."),
    'unknown': _("The health status of the node is unknown."),
}

@register.inclusion_tag(('nodes/status/network_icon.html', 'nodes/status/icon.html'))
def network_status_icon(status, size):
    return {
        'NETWORK_DESCRIPTIONS': NETWORK_DESCRIPTIONS,
        'description': NETWORK_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
        'size': size,
    }

@register.inclusion_tag(('nodes/status/monitored_icon.html', 'nodes/status/icon.html'))
def monitored_status_icon(status, size):
    return {
        'MONITORED_DESCRIPTIONS': MONITORED_DESCRIPTIONS,
        'description': MONITORED_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
        'size': size,
    }

@register.inclusion_tag(('nodes/status/health_icon.html', 'nodes/status/icon.html'))
def health_status_icon(status, size):
    return {
        'HEALTH_DESCRIPTIONS': HEALTH_DESCRIPTIONS,
        'description': HEALTH_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
        'size': size,
    }

@register.inclusion_tag(('nodes/status/network_description.html', 'nodes/status/description.html'))
def network_status_description(status):
    return {
        'NETWORK_DESCRIPTIONS': NETWORK_DESCRIPTIONS,
        'description': NETWORK_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
    }

@register.inclusion_tag(('nodes/status/monitored_description.html', 'nodes/status/description.html'))
def monitored_status_description(status):
    return {
        'MONITORED_DESCRIPTIONS': MONITORED_DESCRIPTIONS,
        'description': MONITORED_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
    }

@register.inclusion_tag(('nodes/status/health_description.html', 'nodes/status/description.html'))
def health_status_description(status):
    return {
        'HEALTH_DESCRIPTIONS': HEALTH_DESCRIPTIONS,
        'description': HEALTH_DESCRIPTIONS[status],
        'status': status,
        # TODO: Use human-readable value from the registry
        'status_display': status,
    }
