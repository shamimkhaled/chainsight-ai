from rest_framework import permissions


class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to the tenant
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if tenant is set in request
        if not hasattr(request, 'tenant') or not request.tenant:
            return False

        # Check if user belongs to the tenant
        return request.user.tenant == request.tenant

    def has_object_permission(self, request, view, obj):
        # Check if object belongs to user's tenant
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user.tenant
        return True


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