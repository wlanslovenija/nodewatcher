from rest_framework import permissions


class EventPermission(permissions.BasePermission):
    """
    Permission class for events.
    """

    def has_object_permission(self, request, view, obj):
        if not obj.related_users:
            return True

        return request.user in obj.related_users
