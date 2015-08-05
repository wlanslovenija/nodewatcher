from django import template

from .. import registration

register = template.Library()


@register.assignment_tag
def registry_get_choices(regpoint_id, choice_id):
    return registration.point(regpoint_id).get_registered_choices(choice_id)


@register.assignment_tag
def registry_get_choice(regpoint_id, choice_id, choice_name):
    return registration.point(regpoint_id).get_registered_choices(choice_id).resolve(choice_name)


@register.simple_tag
def registry_get(root, regpoint, path, field, default=None):
    try:
        return getattr(getattr(root, regpoint).by_registry_id(path), field, default)
    except AttributeError:
        return default
