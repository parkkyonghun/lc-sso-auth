from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...models.user import User
from ...schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationWithSecret,
    ApplicationList
)
from ...services.application_service import ApplicationService
from .auth import require_auth

router = APIRouter(tags=["Applications"])

@router.post("/", response_model=ApplicationWithSecret, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new OAuth application"""
    app_service = ApplicationService(db)
    return app_service.create_application(application_data, str(current_user.id))

@router.get("/", response_model=ApplicationList)
async def list_applications(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of applications per page"),
    search: Optional[str] = Query(None, description="Search applications by name or description"),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List user's OAuth applications"""
    app_service = ApplicationService(db)
    skip = (page - 1) * size
    current_user_id = str(current_user.id)

    if search:
        # Use general search method with user filter
        applications, total = app_service.get_applications(skip=skip, limit=size, search=search)
        # Filter by user
        user_applications = [app for app in applications if str(app.created_by) == current_user_id]
        # Recalculate total for user's applications only
        from sqlalchemy import and_
        from ...models.application import Application
        total_query = app_service.db.query(Application).filter(
            and_(
                Application.created_by == current_user.id,
                Application.name.ilike(f"%{search}%")
            )
        )
        total = total_query.count()
        applications = user_applications
    else:
        # Use user-specific method
        applications, total = app_service.get_applications_by_user(
            user_id=current_user_id,
            skip=skip,
            limit=size
        )

    pages = (total + size - 1) // size  # Calculate total pages

    # Convert ORM objects to Pydantic models
    application_responses = [
        ApplicationResponse(
            id=app.id,
            name=app.name,
            description=app.description,
            client_id=app.client_id,
            redirect_uris=app.get_redirect_uris(),
            allowed_scopes=app.get_allowed_scopes(),
            grant_types=app.get_grant_types(),
            response_types=app.get_response_types(),
            is_active=app.is_active,
            is_confidential=app.is_confidential,
            require_consent=app.require_consent,
            logo_url=app.logo_url,
            website_url=app.website_url,
            privacy_policy_url=app.privacy_policy_url,
            terms_of_service_url=app.terms_of_service_url,
            token_endpoint_auth_method=app.token_endpoint_auth_method,
            access_token_lifetime=app.access_token_lifetime,
            refresh_token_lifetime=app.refresh_token_lifetime,
            created_at=app.created_at,
            updated_at=app.updated_at,
            created_by=app.created_by
        )
        for app in applications
    ]

    return ApplicationList(
        applications=application_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get a specific OAuth application"""
    app_service = ApplicationService(db)
    application = app_service.get_application_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if user owns this application
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to access this application"}
        )
    
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_data: ApplicationUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to update this application"}
        )
    
    return app_service.update_application(application_id, application_data, str(current_user.id))

@router.post("/{application_id}/regenerate-secret", response_model=ApplicationWithSecret)
async def regenerate_client_secret(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Regenerate client secret for an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to regenerate secret for this application"}
        )
    
    return app_service.regenerate_client_secret(application_id, str(current_user.id))

@router.post("/{application_id}/activate")
async def activate_application(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Activate an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to activate this application"
        )
    
    app_service.activate_application(application_id, str(current_user.id))
    return {"message": "Application activated successfully"}

@router.post("/{application_id}/deactivate")
async def deactivate_application(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Deactivate an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to deactivate this application"}
        )
    
    app_service.deactivate_application(application_id, str(current_user.id))
    return {"message": "Application deactivated successfully"}

@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to delete this application"}
        )
    
    app_service.delete_application(application_id, str(current_user.id))
    return {"message": "Application deleted successfully"}

@router.get("/{application_id}/stats")
async def get_application_stats(
    application_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get usage statistics for an OAuth application"""
    app_service = ApplicationService(db)
    
    # Check if application exists and user owns it
    application = app_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to view stats for this application"}
        )
    
    # TODO: Implement actual statistics gathering
    # This would typically include metrics like:
    # - Number of active users
    # - Token usage statistics
    # - API call counts
    # - Error rates
    
    return {
        "application_id": application_id,
        "active_users": 0,
        "total_tokens_issued": 0,
        "api_calls_today": 0,
        "error_rate": 0.0,
        "last_used": None,
        "message": "Statistics feature coming soon"
    }
