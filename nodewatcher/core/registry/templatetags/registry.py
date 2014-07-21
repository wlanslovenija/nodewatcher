from django import template

from .. import registration

register = template.Library()


@register.assignment_tag
def registry_get_choices(regpoint_id, choice_id):
    return registration.point(regpoint_id).get_registered_choices(choice_id)
