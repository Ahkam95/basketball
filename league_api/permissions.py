from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from .constants import USERS

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a admin
        return request.user and request.user.role == USERS['ADMIN']
    
class IsCoach(permissions.BasePermission):
    """
    Custom permission to only allow coach of the game to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a host
        return request.user and request.user.role == USERS['COACH']

class IsPlayer(permissions.BasePermission):
    """
    Custom permission to only allow players of the game to access the view
    """
    def has_permission(self, request, view):
        # Check if the current user is marked as a player
        return request.user and request.user.role == USERS['PLAYER']

class IsAuthenticatedOr401(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)

        if not is_authenticated:
            raise NotAuthenticated()
        return True

class IsAdminOrIsCoach(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admins can access any team
        if request.user.role == USERS['ADMIN']:
            return True
        # Coaches can only access their own team
        if request.user.role == USERS['COACH'] and obj.coach == request.user:
            return True
        return False
    