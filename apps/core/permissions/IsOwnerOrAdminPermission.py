from rest_framework import permissions


class IsOwnerOrAdminPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Returns `True` if the request user is an admin or the owner of the object.
        """
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True

            if request.method in permissions.SAFE_METHODS:
                return True

            return obj == request.user

        return False
