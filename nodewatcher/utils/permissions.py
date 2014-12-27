import itertools

from django import shortcuts
from django.db import models
from django.db.models import query
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes import models as contenttypes_models

from guardian import compat as guardian_compat, exceptions, utils as guardian_utils


def get_users_with_permission(obj, permission_name, with_superusers=False, with_group_users=True):
    """
    Returns queryset of all ``User`` objects with ``permission_name`` object permissions for
    the given ``obj``.

    Similar to `shortcuts.get_users_with_perms`, but instead of `any` object permissions, you
    limit to a permission.

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


def get_objects_for_user(user, perms, klass=None, use_groups=True, any_perm=False, use_superusers=True):
    """
    Returns queryset of objects for which a given ``user`` has *all*
    permissions present at ``perms``.

    Similar to `shortcuts.get_objects_for_user`, but allowing ``perms`` to be an
    empty list to get objects where an user has *any* object permission.

    :param user: ``User`` or ``AnonymousUser`` instance for which objects would
      be returned.
    :param perms: single permission string, or sequence of permission strings
      which should be checked.
      If ``klass`` parameter is not given, those should be full permission
      names rather than only codenames (i.e. ``auth.change_user``). If more than
      one permission is present within sequence, their content type **must** be
      the same or ``MixedContentTypeError`` exception would be raised.
    :param klass: may be a Model, Manager or QuerySet object. If not given
      this parameter would be computed based on given ``params``.
    :param use_groups: if ``False``, wouldn't check user's groups object
      permissions. Default is ``True``.
    :param any_perm: if True, any of permission in sequence is accepted
    :param use_superusers: for superusers return all objects. Default is ``True``.

    :raises MixedContentTypeError: when computed content type for ``perms``
      and/or ``klass`` clashes.
    :raises WrongAppError: if cannot compute app label for given ``perms``/
      ``klass``.

    Example::

        >>> from django.contrib.auth.models import User
        >>> from guardian.shortcuts import get_objects_for_user
        >>> joe = User.objects.get(username='joe')
        >>> get_objects_for_user(joe, 'auth.change_group')
        []
        >>> from guardian.shortcuts import assign_perm
        >>> group = Group.objects.create('some group')
        >>> assign_perm('auth.change_group', joe, group)
        >>> get_objects_for_user(joe, 'auth.change_group')
        [<Group some group>]

    The permission string can also be an iterable. Continuing with the previous example:

        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'])
        []
        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'], any_perm=True)
        [<Group some group>]
        >>> assign_perm('auth.delete_group', joe, group)
        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'])
        [<Group some group>]

    """
    if isinstance(perms, basestring):
        perms = [perms]
    ctype = None
    app_label = None
    codenames = set()

    # Compute codenames set and ctype if possible
    for perm in perms:
        if '.' in perm:
            new_app_label, codename = perm.split('.', 1)
            if app_label is not None and app_label != new_app_label:
                raise exceptions.MixedContentTypeError(
                    "Given perms must have same app label (%s != %s)" % (app_label, new_app_label)
                )
            else:
                app_label = new_app_label
        else:
            codename = perm
        codenames.add(codename)
        if app_label is not None:
            new_ctype = contenttypes_models.ContentType.objects.get(
                app_label=app_label,
                permission__codename=codename,
            )
            if ctype is not None and ctype != new_ctype:
                raise exceptions.MixedContentTypeError(
                    "ContentType was once computed to be %s and another one %s" % (ctype, new_ctype)
                )
            else:
                ctype = new_ctype

    # Compute queryset and ctype if still missing
    if ctype is None and klass is not None:
        queryset = shortcuts._get_queryset(klass)
        ctype = contenttypes_models.ContentType.objects.get_for_model(queryset.model)
    elif ctype is not None and klass is None:
        queryset = shortcuts._get_queryset(ctype.model_class())
    elif klass is None:
        raise exceptions.WrongAppError("Cannot determine content type")
    else:
        queryset = shortcuts._get_queryset(klass)
        if ctype.model_class() != queryset.model:
            raise exceptions.MixedContentTypeError(
                "Content type for given perms and klass differs"
            )

    # At this point, we should have both ctype and queryset and they should
    # match which means: ctype.model_class() == queryset.model
    # we should also have ``codenames`` list

    # First check if user is superuser and if so, return queryset immediately
    if use_superusers and user.is_superuser:
        return queryset

    # Check if the user is anonymous. The
    # django.contrib.auth.models.AnonymousUser object doesn't work for queries
    # and it's nice to be able to pass in request.user blindly.
    if user.is_anonymous():
        user = guardian_utils.get_anonymous_user()

    # Now we should extract list of pk values for which we would filter queryset
    user_model = guardian_utils.get_user_obj_perms_model(queryset.model)
    user_obj_perms_queryset = user_model.objects.filter(
        user=user,
    ).filter(
        permission__content_type=ctype,
    )
    if len(codenames):
        user_obj_perms_queryset = user_obj_perms_queryset.filter(permission__codename__in=codenames)
    if user_model.objects.is_generic():
        fields = ['object_pk', 'permission__codename']
    else:
        fields = ['content_object__pk', 'permission__codename']

    if use_groups:
        group_model = guardian_utils.get_group_obj_perms_model(queryset.model)
        group_filters = {
            'permission__content_type': ctype,
            'group__%s' % guardian_compat.get_user_model().groups.field.related_query_name(): user,
        }
        if len(codenames):
            group_filters.update({
                'permission__codename__in': codenames,
            })
        groups_obj_perms_queryset = group_model.objects.filter(**group_filters)
        if group_model.objects.is_generic():
            fields = ['object_pk', 'permission__codename']
        else:
            fields = ['content_object__pk', 'permission__codename']
        if not any_perm and len(codenames):
            user_obj_perms = user_obj_perms_queryset.values_list(*fields)
            groups_obj_perms = groups_obj_perms_queryset.values_list(*fields)
            data = list(user_obj_perms) + list(groups_obj_perms)
            keyfunc = lambda t: t[0] # sorting/grouping by pk (first in result tuple)
            data = sorted(data, key=keyfunc)
            pk_list = []
            for pk, group in itertools.groupby(data, keyfunc):
                obj_codenames = set((e[1] for e in group))
                if codenames.issubset(obj_codenames):
                    pk_list.append(pk)
            objects = queryset.filter(pk__in=pk_list)
            return objects

    if not any_perm and len(codenames):
        counts = user_obj_perms_queryset.values(fields[0]).annotate(object_pk_count=models.Count(fields[0]))
        user_obj_perms_queryset = counts.filter(object_pk_count__gte=len(codenames))

    q = query.Q(pk__in=user_obj_perms_queryset.values(fields[0]))
    if use_groups:
        q |= query.Q(pk__in=groups_obj_perms_queryset.values(fields[0]))

    return queryset.filter(q)
