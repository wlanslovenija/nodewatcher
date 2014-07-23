from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes import models as contenttypes_models

from guardian import compat as guardian_compat, utils as guardian_utils


def get_users_with_permission(obj, permission_name, with_superusers=False, with_group_users=True):
    """
    Returns queryset of all ``User`` objects with ``permission_name`` object permissions for
    the given ``obj``.

    :param obj: persisted Django's ``Model`` instance
    :param permission_name: permission name to return users for
    :param with_superusers: Default: ``False``. If set to ``True`` result would
      contain all superusers.
    :param with_group_users: Default: ``True``. If set to ``False`` result would
      **not** contain those users who have only group permissions for given ``obj``.
    :return:
    """

    content_type = contenttypes_models.ContentType.objects.get_for_model(obj)
    user_model = guardian_utils.get_user_obj_perms_model(obj)
    related_name = user_model.user.field.related_query_name()
    permission = auth_models.objects.get(content_type=content_type, codename=permission_name)
    if user_model.objects.is_generic():
        user_filters = {
            '%s__content_type' % related_name: content_type,
            '%s__object_pk' % related_name: obj.pk,
            '%s__permission' % related_name: permission,
        }
    else:
        user_filters = {
            '%s__content_object' % related_name: obj,
            '%s__permission' % related_name: permission,
        }
    qset = models.Q(**user_filters)
    if with_group_users:
        group_model = guardian_utils.get_group_obj_perms_model(obj)
        group_rel_name = group_model.group.field.related_query_name()
        if group_model.objects.is_generic():
            group_filters = {
                'groups__%s__content_type' % group_rel_name: content_type,
                'groups__%s__object_pk' % group_rel_name: obj.pk,
                'groups__%s__permission' % group_rel_name: permission,
            }
        else:
            group_filters = {
                'groups__%s__content_object' % group_rel_name: obj,
                'groups__%s__permission' % group_rel_name: permission,
            }
        qset = qset | models.Q(**group_filters)
    if with_superusers:
        qset = qset | models.Q(is_superuser=True)
    return guardian_compat.get_user_model().objects.filter(qset).distinct()
