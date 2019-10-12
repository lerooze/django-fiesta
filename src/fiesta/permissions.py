
from rest_framework import permissions

class IsAgencyUser(permissions.BasePermission):
    """
    Only allow agency users to modify structure metadata
    """

    def has_permission(self, request, view):
        if request.user.agency_member: return True

class IsDataProviderUser(permissions.BasePermission):
    """
    Only allow registrations from data providers
    """

    def has_permission(self, request, view):
        if request.user.data_provider_member: return True
