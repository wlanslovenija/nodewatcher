from django import template
from django.conf import settings

from .. import components

register = template.Library()


# To allow setting a name
class PartialEntries(list):
    pass


@register.assignment_tag(takes_context=True)
def get_partial(context, partial_name):
    try:
        partial = PartialEntries([entry.add_context(context) for entry in components.partials.get_partial(partial_name).entries if entry.is_visible(context['request'], context)])
        partial.name = partial_name
        return partial
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return []


@register.simple_tag(takes_context=True)
def render_partial_entry(context, partial_entry):
    try:
        # We could call partial_entry.add_context(context).render() as well,
        # but the following is performance-wise better
        return partial_entry.render(context)
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return u''
