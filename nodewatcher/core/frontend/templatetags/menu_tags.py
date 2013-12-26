from django import template
from django.conf import settings

from .. import components

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_menu(context, menu_name):
    try:
        return [entry.add_context(context) for entry in components.menus.get_menu(menu_name).get_entries() if entry.is_visible(context['request'])]
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return []


@register.simple_tag(takes_context=True)
def render_menu_entry(context, menu_entry):
    try:
        # We could call menu_entry.add_context(context).render() as well,
        # but the following is performance-wise better
        return menu_entry.render(context)
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return u''
