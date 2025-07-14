from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from ..models.application import Application
from ..schemas.application import ApplicationCreate, ApplicationUpdate
from ..core.security import generate_client_credentials

class ApplicationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_application(self, app_data: ApplicationCreate, created_by: str = None) -> Application:
        """Create a new OAuth application"""
        # Check if application name already exists
        existing_app = self.db.query(Application).filter(
            Application.name == app_data.name
        ).first()
        
        if existing_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application name already exists"
            )
        
        # Generate client credentials
        client_id, client_secret = generate_client_credentials()
        
        # Create new application
        db_app = Application(
            name=app_data.name,
            description=app_data.description,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uris=app_data.redirect_uris,
            allowed_scopes=app_data.allowed_scopes,
            grant_types=app_data.grant_types,
            response_types=app_data.response_types,
            is_confidential=app_data.is_confidential,
            require_consent=app_data.require_consent,
            website_url=str(app_data.website_url) if app_data.website_url else None,
            privacy_policy_url=str(app_data.privacy_policy_url) if app_data.privacy_policy_url else None,
            terms_of_service_url=str(app_data.terms_of_service_url) if app_data.terms_of_service_url else None,
            logo_url=str(app_data.logo_url) if app_data.logo_url else None,
            token_endpoint_auth_method=app_data.token_endpoint_auth_method,
            access_token_lifetime=str(app_data.access_token_lifetime),
            refresh_token_lifetime=str(app_data.refresh_token_lifetime),
            created_by=created_by
        )
        
        self.db.add(db_app)
        self.db.commit()
        self.db.refresh(db_app)
        return db_app
    
    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        """Get application by ID"""
        return self.db.query(Application).filter(Application.id == app_id).first()
    
    def get_application_by_client_id(self, client_id: str) -> Optional[Application]:
        """Get application by client ID"""
        return self.db.query(Application).filter(Application.client_id == client_id).first()
    
    def get_applications_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> tuple[List[Application], int]:
        """Get applications created by a specific user"""
        query = self.db.query(Application).filter(Application.created_by == user_id)
        total = query.count()
        apps = query.offset(skip).limit(limit).all()
        return apps, total
    
    def get_applications(self, skip: int = 0, limit: int = 100, search: str = None) -> tuple[List[Application], int]:
        """Get list of applications with pagination and search"""
        query = self.db.query(Application)
        
        if search:
            search_filter = Application.name.ilike(f"%{search}%")
            query = query.filter(search_filter)
        
        total = query.count()
        apps = query.offset(skip).limit(limit).all()
        return apps, total
    
    def update_application(self, app_id: str, app_data: ApplicationUpdate, user_id: str = None) -> Optional[Application]:
        """Update application information"""
        app = self.get_application_by_id(app_id)
        if not app:
            return None
        
        # Check if user has permission to update this app
        if user_id and app.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this application"
            )
        
        # Check if new name conflicts with existing applications
        if app_data.name and app_data.name != app.name:
            existing_app = self.db.query(Application).filter(
                Application.name == app_data.name,
                Application.id != app_id
            ).first()
            
            if existing_app:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Application name already exists"
                )
        
        # Update fields if provided
        update_data = app_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['website_url', 'privacy_policy_url', 'terms_of_service_url', 'logo_url'] and value:
                setattr(app, field, str(value))
            else:
                setattr(app, field, value)
        
        app.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(app)
        return app
    
    def regenerate_client_secret(self, app_id: str, user_id: str = None) -> Optional[str]:
        """Regenerate client secret for an application"""
        app = self.get_application_by_id(app_id)
        if not app:
            return None
        
        # Check if user has permission to regenerate secret
        if user_id and app.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to regenerate secret for this application"
            )
        
        # Generate new client secret
        _, new_client_secret = generate_client_credentials()
        app.client_secret = new_client_secret
        app.updated_at = datetime.utcnow()
        
        self.db.commit()
        return new_client_secret
    
    def deactivate_application(self, app_id: str, user_id: str = None) -> bool:
        """Deactivate an application"""
        app = self.get_application_by_id(app_id)
        if not app:
            return False
        
        # Check if user has permission to deactivate this app
        if user_id and app.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to deactivate this application"
            )
        
        app.is_active = False
        app.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def activate_application(self, app_id: str, user_id: str = None) -> bool:
        """Activate an application"""
        app = self.get_application_by_id(app_id)
        if not app:
            return False
        
        # Check if user has permission to activate this app
        if user_id and app.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to activate this application"
            )
        
        app.is_active = True
        app.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def delete_application(self, app_id: str, user_id: str = None) -> bool:
        """Delete an application"""
        app = self.get_application_by_id(app_id)
        if not app:
            return False
        
        # Check if user has permission to delete this app
        if user_id and app.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this application"
            )
        
        self.db.delete(app)
        self.db.commit()
        return True
    
    def validate_client_credentials(self, client_id: str, client_secret: str = None) -> Optional[Application]:
        """Validate client credentials"""
        app = self.get_application_by_client_id(client_id)
        if not app or not app.is_active:
            return None
        
        # For confidential clients, verify client secret
        if app.is_confidential and client_secret != app.client_secret:
            return None
        
        return app
    
    def validate_redirect_uri(self, client_id: str, redirect_uri: str) -> bool:
        """Validate if redirect URI is allowed for the client"""
        app = self.get_application_by_client_id(client_id)
        if not app or not app.is_active:
            return False
        
        return app.is_redirect_uri_allowed(redirect_uri)
    
    def validate_scope(self, client_id: str, scope: str) -> bool:
        """Validate if scope is allowed for the client"""
        app = self.get_application_by_client_id(client_id)
        if not app or not app.is_active:
            return False
        
        return app.is_scope_allowed(scope)