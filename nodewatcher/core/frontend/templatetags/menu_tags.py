from django import template
from django.conf import settings

from .. import components

register = template.Library()


# To allow setting a name
class MenuEntries(list):
    pass


@register.assignment_tag(takes_context=True)
def get_menu(context, menu_name):
    try:
        menu = MenuEntries([
            entry.add_context(context)
            for entry in components.menus.get_menu(menu_name).entries
            if entry.is_visible(context['request'], context)
        ])
        menu.name = menu_name
        return menu
    except:
        if settings.DEBUG:
            raise
        return []


@register.simple_tag(takes_context=True)
def render_menu_entry(context, menu_entry):
    try:
        # We could call menu_entry.add_context(context).render() as well,
        # but the following is performance-wise better
        return menu_entry.render(context)
    except:
        if settings.DEBUG:
            raise
        return u''
