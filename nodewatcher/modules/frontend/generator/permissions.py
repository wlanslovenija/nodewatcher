from rest_framework import permissions


class BuildResultPermission(permissions.BasePermission):
    """
    Permission class for build results.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
