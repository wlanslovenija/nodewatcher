from django import template

register = template.Library()

@register.inclusion_tag(('generator/status_icon.html'))
def generator_status_icon(choice, size):
    return {
        'choice': choice,
        'size': size,
    }
