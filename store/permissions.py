from rest_framework import permissions


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """
    A permission class that allows owners, staff, and authenticated users to perform safe methods.

    Methods:
        has_object_permission: Checks if the user has permission to perform the request.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and (request.user == obj.owner or request.user.is_staff)
        )
