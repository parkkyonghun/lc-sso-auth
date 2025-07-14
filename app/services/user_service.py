from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from datetime import datetime

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, PasswordChange
from ..core.security import hash_password, verify_password

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        existing_user = self.db.query(User).filter(
            or_(User.username == user_data.username, User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                detail = "Username already registered"
            else:
                detail = "Email already registered"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_superuser=user_data.is_superuser
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        if not user:
            return None
        
        # Check if account is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed login attempts"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.increment_failed_attempts()
            self.db.commit()
            return None
        
        # Reset failed attempts on successful login
        user.reset_failed_attempts()
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        self.db.commit()
        return user
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def activate_user(self, user_id: str) -> bool:
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def verify_user(self, user_id: str) -> bool:
        """Mark user as verified"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_users(self, skip: int = 0, limit: int = 100, search: str = None) -> tuple[List[User], int]:
        """Get list of users with pagination and search"""
        query = self.db.query(User)
        
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user account (soft delete by deactivating)"""
        return self.deactivate_user(user_id)