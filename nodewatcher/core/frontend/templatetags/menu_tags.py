from django import template
from django.conf import settings

from ..components import menu

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_menu(context, menu_name):
    try:
        return [entry for entry in menu.known_menus[menu_name].get_entries() if entry.has_permission(context['request'])]
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return []
