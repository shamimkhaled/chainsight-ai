from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to check if user is admin
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is manager or admin
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner of the object or admin
    """

    def has_object_permission(self, request, view, obj):
        # Allow admin users to do anything
        if request.user.role == 'admin':
            return True

        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False