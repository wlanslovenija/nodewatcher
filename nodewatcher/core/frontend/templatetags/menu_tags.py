from django import template
from django.conf import settings

from .. import components

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_menu(context, menu_name):
    try:
        return [entry.add_context(context) for entry in components.menus.get_menu(menu_name).get_entries() if entry.has_permission(context['request'])]
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return []
