# Pending permissions.
_pending_permissions = []


def register(model, codename, name):
    """
    Dynamically adds a new permission into an existing model.
    """

    _pending_permissions.append((model, codename, name))


def get_all_permissions():
    """
    Return all permissions that should be registered.
    """

    return _pending_permissions


def create_permissions(**kwargs):
    """
    Create all registered permissions in the database.
    """

    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    for model, codename, name in get_all_permissions():
        content_type = ContentType.objects.get_for_model(model)
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
