from rest_framework import permissions

class IsManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow managers or admins to approve/reject requests
    """
    def has_permission(self, request, view):
        roles = getattr(request.user, 'roles', [])
        return 'ROLE_ADMIN' in roles or 'ROLE_MANAGER' in roles

class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a leave request or managers/admins to view it
    """
    def has_object_permission(self, request, view, obj):
        roles = getattr(request.user, 'roles', [])
        
        # Managers and admins can access all requests
        if 'ROLE_ADMIN' in roles or 'ROLE_MANAGER' in roles:
            return True
            
        # Check if user is the owner of the request
        return obj.employee.user_id == request.user.id
