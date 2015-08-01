from django import template


register = template.Library()


@register.inclusion_tag(('nodes/status/network_icon.html', 'nodes/status/icon.html'))
def network_status_icon(choice, size):
    return {
        'category' : 'network',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('nodes/status/monitored_icon.html', 'nodes/status/icon.html'))
def monitored_status_icon(choice, size):
    return {
        'category' : 'monitored',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('nodes/status/health_icon.html', 'nodes/status/icon.html'))
def health_status_icon(choice, size):
    return {
        'category' : 'health',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('nodes/status/network_description.html', 'nodes/status/description.html'))
def network_status_description(choice):
    return {
        'category' : 'network',
        'choice': choice,
    }


@register.inclusion_tag(('nodes/status/monitored_description.html', 'nodes/status/description.html'))
def monitored_status_description(choice):
    return {
        'category' : 'monitored',
        'choice': choice,
    }


@register.inclusion_tag(('nodes/status/health_description.html', 'nodes/status/description.html'))
def health_status_description(choice):
    return {
        'category' : 'health',
        'choice': choice,
    }
