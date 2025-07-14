from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from ..models.user import User
from ..models.application import Application
from ..models.role import Role
from ..models.permission import Permission
from ..schemas.admin import (
    SystemStatsResponse, UserStatsResponse, AdminUserUpdate,
    AdminApplicationUpdate, AdminUserCreate
)
from ..core.security import hash_password
from .user_service import UserService
from .application_service import ApplicationService

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.app_service = ApplicationService(db)
        from .permission_service import PermissionService
        self.permission_service = PermissionService(db)
    
    def verify_admin_access(self, user_id: str) -> bool:
        """Verify if user has admin access"""
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Superuser always has access
        if user.is_superuser:
            return True
        
        # Check if user has any admin-level permissions
        admin_permissions = [
            "manage_permissions", "create_roles", "edit_roles", "delete_roles",
            "create_users", "delete_users", "manage_user_roles"
        ]
        
        if self.permission_service.user_has_any_permission(user_id, admin_permissions):
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    def verify_permission(self, user_id: str, permission: str) -> bool:
        """Verify if user has specific permission"""
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if not self.permission_service.user_has_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return True
    
    def get_system_stats(self, admin_user_id: str) -> SystemStatsResponse:
        """Get comprehensive system statistics"""
        self.verify_admin_access(admin_user_id)
        
        # User statistics
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        
        # Recent user registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # Application statistics
        total_applications = self.db.query(Application).count()
        active_applications = self.db.query(Application).filter(
            Application.is_active == True
        ).count()
        
        # Recent applications (last 30 days)
        recent_applications = self.db.query(Application).filter(
            Application.created_at >= thirty_days_ago
        ).count()
        
        # Security statistics
        locked_users = self.db.query(User).filter(
            User.lockout_until.isnot(None),
            User.lockout_until > datetime.utcnow()
        ).count()
        
        unverified_users = self.db.query(User).filter(
            User.is_verified == False
        ).count()
        
        return SystemStatsResponse(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            recent_registrations=recent_registrations,
            total_applications=total_applications,
            active_applications=active_applications,
            recent_applications=recent_applications,
            locked_users=locked_users,
            unverified_users=unverified_users)
    
    # Role and Permission Management Methods
    def assign_role_to_user(self, admin_user_id: str, user_id: str, role_name: str) -> bool:
        """Assign a role to a user"""
        self.verify_permission(admin_user_id, "manage_user_roles")
        return self.permission_service.assign_role_to_user(user_id, role_name)
    
    def remove_role_from_user(self, admin_user_id: str, user_id: str, role_name: str) -> bool:
        """Remove a role from a user"""
        self.verify_permission(admin_user_id, "manage_user_roles")
        return self.permission_service.remove_role_from_user(user_id, role_name)
    
    def get_user_roles(self, admin_user_id: str, user_id: str) -> List[str]:
        """Get all roles assigned to a user"""
        self.verify_permission(admin_user_id, "view_users")
        return self.permission_service.get_user_roles(user_id)
    
    def get_user_permissions(self, admin_user_id: str, user_id: str) -> List[str]:
        """Get all permissions for a user"""
        self.verify_permission(admin_user_id, "view_users")
        return self.permission_service.get_user_permissions(user_id)
    
    def get_all_roles(self, admin_user_id: str) -> List[dict]:
        """Get all available roles"""
        self.verify_permission(admin_user_id, "view_roles")
        roles = self.db.query(Role).all()
        return [{
            "id": role.id,
            "role_name": role.role_name,
            "description": role.description,
            "permissions": [p.permission_name for p in role.permissions]
        } for role in roles]
    
    def get_all_permissions(self, admin_user_id: str) -> List[dict]:
        """Get all available permissions"""
        self.verify_permission(admin_user_id, "view_permissions")
        return self.permission_service.get_all_permissions()
    
    def get_user_stats(self, admin_user_id: str) -> UserStatsResponse:
        """Get detailed user statistics"""
        self.verify_admin_access(admin_user_id)
        
        # User registration trends (last 12 months)
        registration_trends = []
        for i in range(12):
            start_date = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
            end_date = start_date + timedelta(days=30)
            
            count = self.db.query(User).filter(
                and_(
                    User.created_at >= start_date,
                    User.created_at < end_date
                )
            ).count()
            
            registration_trends.append({
                "month": start_date.strftime("%Y-%m"),
                "registrations": count
            })
        
        registration_trends.reverse()
        
        # Top active users (by last login)
        active_users = self.db.query(User).filter(
            User.last_login.isnot(None)
        ).order_by(desc(User.last_login)).limit(10).all()
        
        top_users = [{
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "last_login": user.last_login.isoformat() if user.last_login else None
        } for user in active_users]
        
        return UserStatsResponse(
            registration_trends=registration_trends,
            top_active_users=top_users
        )
    
    def search_users(self, admin_user_id: str, query: str, skip: int = 0, limit: int = 50) -> tuple[List[User], int]:
        """Advanced user search for admins"""
        self.verify_permission(admin_user_id, "view_users")
        
        db_query = self.db.query(User)
        
        if query:
            search_filter = func.lower(User.username).contains(query.lower()) | \
                          func.lower(User.email).contains(query.lower()) | \
                          func.lower(User.full_name).contains(query.lower())
            db_query = db_query.filter(search_filter)
        
        total = db_query.count()
        users = db_query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        return users, total
    
    def create_user_as_admin(self, admin_user_id: str, user_data: AdminUserCreate) -> User:
        """Create a new user with admin privileges"""
        self.verify_permission(admin_user_id, "create_users")
        
        # Check if username or email already exists
        existing_user = self.db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified,
            is_superuser=user_data.is_superuser
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user_as_admin(self, admin_user_id: str, user_id: str, user_data: AdminUserUpdate) -> Optional[User]:
        """Update user with admin privileges"""
        self.verify_permission(admin_user_id, "edit_users")
        
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        update_data = user_data.dict(exclude_unset=True)
        
        # Handle password update
        if 'password' in update_data:
            update_data['hashed_password'] = hash_password(update_data.pop('password'))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user_as_admin(self, admin_user_id: str, user_id: str) -> bool:
        """Permanently delete user (admin only)"""
        self.verify_permission(admin_user_id, "delete_users")
        
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return False
        
        # Prevent admin from deleting themselves
        if user_id == admin_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def get_all_applications(self, admin_user_id: str, skip: int = 0, limit: int = 50) -> tuple[List[Application], int]:
        """Get all applications (admin view)"""
        self.verify_admin_access(admin_user_id)
        
        query = self.db.query(Application)
        total = query.count()
        apps = query.order_by(desc(Application.created_at)).offset(skip).limit(limit).all()
        
        return apps, total
    
    def update_application_as_admin(self, admin_user_id: str, app_id: str, app_data: AdminApplicationUpdate) -> Optional[Application]:
        """Update application with admin privileges"""
        self.verify_admin_access(admin_user_id)
        
        app = self.app_service.get_application_by_id(app_id)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update fields if provided
        update_data = app_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(app, field, value)
        
        app.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(app)
        return app
    
    def delete_application_as_admin(self, admin_user_id: str, app_id: str) -> bool:
        """Delete application (admin only)"""
        self.verify_admin_access(admin_user_id)
        
        app = self.app_service.get_application_by_id(app_id)
        if not app:
            return False
        
        self.db.delete(app)
        self.db.commit()
        return True
    
    def unlock_user_account(self, admin_user_id: str, user_id: str) -> bool:
        """Unlock a locked user account"""
        self.verify_admin_access(admin_user_id)
        
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return False
        
        user.lockout_until = None
        user.failed_login_attempts = 0
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_recent_activities(self, admin_user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system activities"""
        self.verify_admin_access(admin_user_id)
        
        activities = []
        
        # Recent user registrations
        recent_users = self.db.query(User).order_by(desc(User.created_at)).limit(limit // 2).all()
        for user in recent_users:
            activities.append({
                "type": "user_registration",
                "timestamp": user.created_at.isoformat(),
                "description": f"New user registered: {user.username}",
                "user_id": str(user.id)
            })
        
        # Recent application registrations
        recent_apps = self.db.query(Application).order_by(desc(Application.created_at)).limit(limit // 2).all()
        for app in recent_apps:
            activities.append({
                "type": "application_registration",
                "timestamp": app.created_at.isoformat(),
                "description": f"New application registered: {app.name}",
                "application_id": str(app.id)
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        return activities[:limit]

    # Role Management Methods
    def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        return self.db.query(Role).all()

    def create_role(self, role_name: str, description: str = None, permissions: List[str] = None) -> Role:
        """Create a new role"""
        # Check if role already exists
        existing_role = self.db.query(Role).filter(Role.role_name == role_name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )

        role = Role(role_name=role_name, description=description)
        self.db.add(role)
        self.db.flush()  # Get the ID

        # Add permissions if provided
        if permissions:
            for perm_name in permissions:
                permission = self.db.query(Permission).filter(Permission.permission_name == perm_name).first()
                if permission:
                    role.permissions.append(permission)

        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: str, update_data: Dict[str, Any]) -> Optional[Role]:
        """Update a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None

        # Update basic fields
        if 'role_name' in update_data:
            role.role_name = update_data['role_name']
        if 'description' in update_data:
            role.description = update_data['description']

        # Update permissions if provided
        if 'permissions' in update_data:
            role.permissions.clear()
            for perm_name in update_data['permissions']:
                permission = self.db.query(Permission).filter(Permission.permission_name == perm_name).first()
                if permission:
                    role.permissions.append(permission)

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False

        # Check if role is assigned to any users
        users_with_role = self.db.query(User).filter(User.roles.contains(role)).count()
        if users_with_role > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete role that is assigned to users"
            )

        self.db.delete(role)
        self.db.commit()
        return True

    # Permission Management Methods
    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions"""
        return self.db.query(Permission).all()

    def create_permission(self, permission_name: str, description: str = None) -> Permission:
        """Create a new permission"""
        # Check if permission already exists
        existing_perm = self.db.query(Permission).filter(Permission.permission_name == permission_name).first()
        if existing_perm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )

        permission = Permission(permission_name=permission_name, description=description)
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission"""
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            return False

        # Check if permission is assigned to any roles
        roles_with_permission = self.db.query(Role).filter(Role.permissions.contains(permission)).count()
        if roles_with_permission > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete permission that is assigned to roles"
            )

        self.db.delete(permission)
        self.db.commit()
        return True