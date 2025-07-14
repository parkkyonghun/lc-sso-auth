from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import User
from ..models.role import Role
from ..models.permission import Permission


class PermissionService:
    """Service for managing permissions and role-based access control"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user based on their roles"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Superuser has all permissions
        if user.is_superuser:
            return [p.permission_name for p in self.db.query(Permission).all()]
        
        # Get permissions from user's roles
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.permission_name)
        
        return list(permissions)
    
    def user_has_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        user_permissions = self.get_user_permissions(user_id)
        return permission_name in user_permissions
    
    def user_has_any_permission(self, user_id: str, permission_names: List[str]) -> bool:
        """Check if user has any of the specified permissions"""
        user_permissions = self.get_user_permissions(user_id)
        return any(perm in user_permissions for perm in permission_names)
    
    def user_has_all_permissions(self, user_id: str, permission_names: List[str]) -> bool:
        """Check if user has all of the specified permissions"""
        user_permissions = self.get_user_permissions(user_id)
        return all(perm in user_permissions for perm in permission_names)
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.roles
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or role not found"
            )
        
        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
            return True
        return False
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or role not found"
            )
        
        if role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            return True
        return False
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all available permissions"""
        return self.db.query(Permission).order_by(Permission.category, Permission.permission_name).all()
    
    def get_permissions_by_category(self) -> Dict[str, List[Permission]]:
        """Get permissions grouped by category"""
        permissions = self.get_all_permissions()
        categorized = {}
        
        for permission in permissions:
            category = permission.category or "General"
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(permission)
        
        return categorized
    
    def create_permission(self, permission_name: str, description: str = None, category: str = None) -> Permission:
        """Create a new permission"""
        # Check if permission already exists
        existing = self.db.query(Permission).filter(Permission.permission_name == permission_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )
        
        permission = Permission(
            permission_name=permission_name,
            description=description,
            category=category
        )
        
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        
        return permission
    
    def update_permission(self, permission_id: str, permission_name: str = None, 
                         description: str = None, category: str = None) -> Optional[Permission]:
        """Update an existing permission"""
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        if permission_name and permission_name != permission.permission_name:
            # Check if new name already exists
            existing = self.db.query(Permission).filter(
                Permission.permission_name == permission_name,
                Permission.id != permission_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Permission name already exists"
                )
            permission.permission_name = permission_name
        
        if description is not None:
            permission.description = description
        
        if category is not None:
            permission.category = category
        
        self.db.commit()
        self.db.refresh(permission)
        
        return permission
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission"""
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        self.db.delete(permission)
        self.db.commit()
        
        return True
    
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """Assign a permission to a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role or permission not found"
            )
        
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
            return True
        return False
    
    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Remove a permission from a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not role or not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role or permission not found"
            )
        
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
            return True
        return False


# Permission decorators for route protection
def require_permission(permission_name: str):
    """Decorator to require specific permission for route access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be used with FastAPI dependencies
            # Implementation depends on how you want to integrate with your auth system
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permission_names: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_names: List[str]):
    """Decorator to require all of the specified permissions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator