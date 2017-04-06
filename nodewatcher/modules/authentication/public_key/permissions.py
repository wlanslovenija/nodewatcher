from rest_framework import permissions


class UserAuthenticationKeyPermission(permissions.BasePermission):
    """
    Permission class for user authentication keys.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
