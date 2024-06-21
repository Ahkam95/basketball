from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a admin
        return request.user and request.user.role == 'admin'
    
class IsCoach(permissions.BasePermission):
    """
    Custom permission to only allow coach of the game to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a host
        return request.user and request.user.role == 'coach'

class IsPlayer(permissions.BasePermission):
    """
    Custom permission to only allow players of the game to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a player
        return request.user and request.user.role == 'player'

class IsAuthenticatedOr401(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)

        if not is_authenticated:
            raise NotAuthenticated()
        return True
