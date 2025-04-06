from functools import wraps
from rest_framework.exceptions import PermissionDenied
from users.models import User, Hierarchy


def check_role_permission(required_roles=None, owner_field=None, assignee_field=None):
    """
    Decorator to check if a user has permission to access a resource based on their role
    and relationship to the object (e.g., owner, assignee, manager of assignee).
    
    Parameters:
    - required_roles: List of roles that always have access (e.g., SUPER_MANAGER)
    - owner_field: Field name in the object that refers to the owner
    - assignee_field: Field name in the object that refers to the assignee
    
    This can be applied to view methods that receive a request and object.
    """
    if required_roles is None:
        required_roles = [User.Role.SUPER_MANAGER]
    
    def decorator(view_method):
        @wraps(view_method)
        def wrapped_view(self, request, *args, **kwargs):
            # Get the object (this assumes object has already been retrieved,
            # typically in a get_object method of a view)
            obj = self.get_object()
            
            user = request.user
            
            # Always allow users with required roles
            if user.role in required_roles:
                return view_method(self, request, *args, **kwargs)
            
            # Check if user is the owner
            if owner_field and hasattr(obj, owner_field):
                owner = getattr(obj, owner_field)
                if owner == user:
                    return view_method(self, request, *args, **kwargs)
            
            # Check if user is the assignee
            if assignee_field and hasattr(obj, assignee_field):
                assignee = getattr(obj, assignee_field)
                if assignee == user:
                    return view_method(self, request, *args, **kwargs)
            
            # Check if user is a manager of the assignee
            if assignee_field and hasattr(obj, assignee_field):
                assignee = getattr(obj, assignee_field)
                if assignee and user.role == User.Role.MANAGER:
                    # Check if assignee reports to this manager
                    is_manager = Hierarchy.objects.filter(
                        manager=user,
                        collection_officer=assignee
                    ).exists()
                    if is_manager:
                        return view_method(self, request, *args, **kwargs)
            
            # Deny access if none of the conditions are met
            raise PermissionDenied("You do not have permission to perform this action.")
        
        return wrapped_view
    
    return decorator


def has_object_permission(user, obj, owner_field=None, assignee_field=None, required_roles=None):
    """
    Function to check if a user has permission to access a specific object.
    This can be used in object-level permission checks in viewsets or views.
    
    Parameters:
    - user: The user requesting access
    - obj: The object being accessed
    - owner_field: Field name in the object that refers to the owner
    - assignee_field: Field name in the object that refers to the assignee
    - required_roles: List of roles that always have access (e.g., SUPER_MANAGER)
    
    Returns:
    - Boolean indicating whether the user has permission
    """
    if required_roles is None:
        required_roles = [User.Role.SUPER_MANAGER]
    
    # Always allow users with required roles
    if user.role in required_roles:
        return True
    
    # Check if user is the owner
    if owner_field and hasattr(obj, owner_field):
        owner = getattr(obj, owner_field)
        if owner == user:
            return True
    
    # Check if user is the assignee
    if assignee_field and hasattr(obj, assignee_field):
        assignee = getattr(obj, assignee_field)
        if assignee == user:
            return True
    
    # Check if user is a manager of the assignee
    if assignee_field and hasattr(obj, assignee_field):
        assignee = getattr(obj, assignee_field)
        if assignee and user.role == User.Role.MANAGER:
            # Check if assignee reports to this manager
            is_manager = Hierarchy.objects.filter(
                manager=user,
                collection_officer=assignee
            ).exists()
            if is_manager:
                return True
    
    # Deny access if none of the conditions are met
    return False


class DynamicPermission:
    """
    A class that can be instantiated to create custom permission checks
    with specific role and field requirements.
    
    This can be used as a permission class in DRF views.
    """
    
    def __init__(self, required_roles=None, owner_field=None, assignee_field=None):
        self.required_roles = required_roles or [User.Role.SUPER_MANAGER]
        self.owner_field = owner_field
        self.assignee_field = assignee_field
    
    def has_permission(self, request, view):
        # Always require authentication
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        return has_object_permission(
            user=request.user,
            obj=obj,
            owner_field=self.owner_field,
            assignee_field=self.assignee_field,
            required_roles=self.required_roles
        ) 