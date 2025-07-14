from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationWithSecret,
    ApplicationList
)
from ..services.application_service import ApplicationService
from .auth import require_auth

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationWithSecret, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user_id: str = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new OAuth application"""
    app_service = ApplicationService(db)
    return app_service.create_application(application_data, current_user_id)

@router.get("/", response_model=ApplicationList)
async def list_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of applications to return"),
    search: Optional[str] = Query(None, description="Search applications by name or description"),
    current_user_id: str = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List user's OAuth applications"""
    app_service = ApplicationService(db)
    applications, total = app_service.list_applications(
        user_id=current_user_id,
        skip=skip,
        limit=limit,
        search=search
    )
    
    return ApplicationList(
        applications=applications,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to access this application"}
        )
    
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_data: ApplicationUpdate,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to update this application"}
        )
    
    return app_service.update_application(application_id, application_data, current_user_id)

@router.post("/{application_id}/regenerate-secret", response_model=ApplicationWithSecret)
async def regenerate_client_secret(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to regenerate secret for this application"}
        )
    
    return app_service.regenerate_client_secret(application_id, current_user_id)

@router.post("/{application_id}/activate")
async def activate_application(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to activate this application"
        )
    
    app_service.activate_application(application_id, current_user_id)
    return {"message": "Application activated successfully"}

@router.post("/{application_id}/deactivate")
async def deactivate_application(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to deactivate this application"}
        )
    
    app_service.deactivate_application(application_id, current_user_id)
    return {"message": "Application deactivated successfully"}

@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "detail": "You don't have permission to delete this application"}
        )
    
    app_service.delete_application(application_id, current_user_id)
    return {"message": "Application deleted successfully"}

@router.get("/{application_id}/stats")
async def get_application_stats(
    application_id: str,
    current_user_id: str = Depends(require_auth),
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
    
    if application.owner_id != current_user_id:
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