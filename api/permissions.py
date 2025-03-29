from rest_framework import permissions
from users.models import User


class IsSuperManager(permissions.BasePermission):
    """
    Permission to only allow Super Managers to access the view.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.SUPER_MANAGER)


class IsManagerOrSuperManager(permissions.BasePermission):
    """
    Permission to only allow Managers and Super Managers to access the view.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [User.Role.MANAGER, User.Role.SUPER_MANAGER]
        )


class IsCollectionOfficerOrAbove(permissions.BasePermission):
    """
    Permission to allow Collection Officers, Managers, and Super Managers to access the view.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [
                User.Role.COLLECTION_OFFICER,
                User.Role.MANAGER, 
                User.Role.SUPER_MANAGER
            ]
        )


class IsCallingAgentOrAbove(permissions.BasePermission):
    """
    Permission to allow Calling Agents and all higher roles to access the view.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [
                User.Role.CALLING_AGENT,
                User.Role.COLLECTION_OFFICER,
                User.Role.MANAGER, 
                User.Role.SUPER_MANAGER
            ]
        )


class CustomerAccessPermission(permissions.BasePermission):
    """
    Permission class for Customer model:
    - Super Managers and Managers can access all customers
    - Collection Officers can access only their assigned customers
    - Calling Agents have read-only access to customers
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Super Managers and Managers have full access
        if request.user.role in [User.Role.SUPER_MANAGER, User.Role.MANAGER]:
            return True
        
        # Collection Officers can only access their assigned customers
        if request.user.role == User.Role.COLLECTION_OFFICER:
            # For list/retrieve operations, allow access to assigned customers
            if request.method in permissions.SAFE_METHODS:
                return obj.assigned_officer == request.user
            # For create/update/delete, only allow if they're the assigned officer
            return obj.assigned_officer == request.user
        
        # Calling Agents have read-only access
        if request.user.role == User.Role.CALLING_AGENT:
            return request.method in permissions.SAFE_METHODS
        
        return False


class LoanAccessPermission(permissions.BasePermission):
    """
    Permission class for Loan model:
    - Super Managers and Managers can access all loans
    - Collection Officers can access only their assigned loans
    - Calling Agents have read-only access to loans they're allowed to work with
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Super Managers and Managers have full access
        if request.user.role in [User.Role.SUPER_MANAGER, User.Role.MANAGER]:
            return True
        
        # Collection Officers can only access their assigned loans
        if request.user.role == User.Role.COLLECTION_OFFICER:
            # Allow read access for any loan where they're assigned to the customer
            if request.method in permissions.SAFE_METHODS:
                return (obj.assigned_officer == request.user or 
                        obj.customer.assigned_officer == request.user)
            # For create/update/delete, only allow if they're the assigned officer
            return obj.assigned_officer == request.user
        
        # Calling Agents have read-only access
        if request.user.role == User.Role.CALLING_AGENT:
            if request.method in permissions.SAFE_METHODS:
                # Check if this customer is in a list they're allowed to access
                # This would need a more sophisticated check in a real implementation
                return True
            return False
        
        return False


class InteractionAndFollowUpPermission(permissions.BasePermission):
    """
    Permission class for Interaction and FollowUp models:
    - Super Managers and Managers can access all interactions/follow-ups
    - Collection Officers can access only interactions/follow-ups related to their customers
    - Calling Agents can access/create interactions for customers they're working with
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Super Managers and Managers have full access
        if request.user.role in [User.Role.SUPER_MANAGER, User.Role.MANAGER]:
            return True
        
        # Collection Officers
        if request.user.role == User.Role.COLLECTION_OFFICER:
            # Check if this customer is assigned to the collection officer
            return obj.customer.assigned_officer == request.user
        
        # Calling Agents - They can create and view interactions for their assigned work
        if request.user.role == User.Role.CALLING_AGENT:
            # Allow reading interactions they initiated
            if request.method in permissions.SAFE_METHODS:
                if hasattr(obj, 'initiated_by'):  # For Interaction model
                    return obj.initiated_by == request.user
                elif hasattr(obj, 'created_by'):  # For FollowUp model
                    return obj.created_by == request.user
            
            # For creating/updating, check if they initiated/created it
            if hasattr(obj, 'initiated_by'):  # For Interaction model
                return obj.initiated_by == request.user
            elif hasattr(obj, 'created_by'):  # For FollowUp model
                return obj.created_by == request.user
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is the owner
        return obj.user == request.user 