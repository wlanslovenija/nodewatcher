from django import template


register = template.Library()


@register.inclusion_tag(('status/network_icon.html', 'status/icon.html'))
def network_status_icon(choice, size):
    return {
        'category': 'network',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('status/monitored_icon.html', 'status/icon.html'))
def monitored_status_icon(choice, size):
    return {
        'category': 'monitored',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('status/health_icon.html', 'status/icon.html'))
def health_status_icon(choice, size):
    return {
        'category': 'health',
        'choice': choice,
        'size': size,
    }


@register.inclusion_tag(('status/network_description.html', 'status/description.html'))
def network_status_description(choice):
    return {
        'category': 'network',
        'choice': choice,
    }


@register.inclusion_tag(('status/monitored_description.html', 'status/description.html'))
def monitored_status_description(choice):
    return {
        'category': 'monitored',
        'choice': choice,
    }


@register.inclusion_tag(('status/health_description.html', 'status/description.html'))
def health_status_description(choice):
    return {
        'category': 'health',
        'choice': choice,
    }
