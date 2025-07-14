"""
Authentication utilities for Flask Admin Panel
"""



from functools import wraps
from flask import session, redirect, url_for, request, flash

from app.core.database import get_db
from app.services.permission_service import PermissionService


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('main.login', next=request.url))

        # Check if token is still valid by checking user data
        if not session.get('user'):
            flash('Session expired. Please login again.', 'warning')
            return redirect(url_for('main.logout'))
        
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """Decorator to require super admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('main.login', next=request.url))

        user = session.get('user', {})
        if not user.get('is_superuser'):
            flash('Super admin privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges (superuser or admin role)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('main.login', next=request.url))

        user = session.get('user', {})
        if not (user.get('is_superuser') or has_admin_role(user)):
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def has_permission(user: dict, permission: str) -> bool:
    """Check if user has specific permission"""
    if user.get('is_superuser'):
        return True
    
    user_permissions = user.get('permissions', [])
    return permission in user_permissions


def has_admin_role(user: dict) -> bool:
    """Check if user has admin role"""
    user_roles = user.get('roles', [])
    admin_roles = ['Admin', 'Application Admin']
    return any(role in admin_roles for role in user_roles)


def get_user_permissions(user: dict) -> list:
    """Get all permissions for a user"""
    if user.get('is_superuser'):
        # Superuser has all permissions
        try:
            db = next(get_db())
            permission_service = PermissionService(db)
            return [p.permission_name for p in permission_service.get_all_permissions()]
        except Exception:
            return []
    return user.get('permissions', [])


def can_access_route(user: dict, route_name: str) -> bool:
    """Check if user can access a specific route"""
    # Route permission mapping
    route_permissions = {
        'users': 'view_users',
        'create_user': 'edit_users',
        'edit_user': 'edit_users',
        'delete_user': 'delete_users',
        'applications': 'view_applications',
        'create_application': 'edit_applications',
        'edit_application': 'edit_applications',
        'delete_application': 'delete_applications',
        'roles': 'manage_roles',
        'permissions': 'manage_roles',
    }
    
    required_permission = route_permissions.get(route_name)
    if not required_permission:
        # If no specific permission required, allow access for logged-in users
        return True
    
    return has_permission(user, required_permission)


def get_user_role_names(user: dict) -> list:
    """Get user role names"""
    return user.get('roles', [])


def is_readonly_user(user: dict) -> bool:
    """Check if user has read-only access"""
    if user.get('is_superuser'):
        return False
    
    user_permissions = get_user_permissions(user)
    write_permissions = ['edit_users', 'delete_users', 'edit_applications', 'delete_applications', 'manage_roles']
    
    return not any(perm in user_permissions for perm in write_permissions)
