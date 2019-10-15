
from rest_framework import permissions

class HasMaintainablePermission(permissions.BasePermission):
    """
    Only allow users with the maintainable pemission maintainable artefacts CRUDs
    """
    def has_permission(self, request, view):
        if request.user.has_perm('registry.maintainable'): return True
