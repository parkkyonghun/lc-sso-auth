from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from ..models.user import User
from ..core.database import get_db
from ..core.security import create_session, get_session, delete_session, decode_jwt, check_rate_limit
from ..schemas.user import UserCreate, UserResponse, UserUpdate, PasswordChange
from ..services.user_service import UserService

router = APIRouter(tags=["Authentication"])
security = HTTPBearer(auto_error=False)
templates = Jinja2Templates(directory="templates")

def get_current_user(
    request: Request, 
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from session or token"""
    user_id = None
    
    # Try session first
    session_id = request.cookies.get("session_id")
    if session_id:
        session_data = get_session(session_id)
        if session_data:
            user_id = session_data.get("user_id")
    
    # If no session, try token
    if not user_id and credentials:
        try:
            payload = decode_jwt(credentials.credentials)
            if payload.get("token_type") == "access_token":
                user_id = payload.get("sub")
        except Exception:
            pass  # Ignore token errors
            
    if not user_id:
        return None
        
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)

def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication and return user object"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip, "register", limit=5, window=3600):  # 5 registrations per hour
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user

@router.post("/login")
async def login(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """User login"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip, "login", limit=10, window=900):  # 10 attempts per 15 minutes
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    user_service = UserService(db)
    user = user_service.authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create session
    session_id = create_session(str(user.id))
    
    # --- Begin: API client detection and JSON response ---
    accept_header = request.headers.get("accept", "")
    x_requested_with = request.headers.get("x-requested-with", "")
    is_api_client = accept_header.lower() == "application/json" or x_requested_with.lower() == "xmlhttprequest"
    if is_api_client:
        from ..core.security import create_access_token
        access_token = create_access_token(str(user.id))
        return {"access_token": access_token, "token_type": "bearer", "user": {"id": str(user.id), "username": user.username, "email": user.email, "is_superuser": user.is_superuser}}
    # --- End: API client detection and JSON response ---
    
    # Check if this is a redirect from OAuth flow
    next_url = request.query_params.get("next")
    if next_url:
        response = RedirectResponse(url=next_url, status_code=302)
    else:
        response = RedirectResponse(url="/api/v1/admin/dashboard", status_code=302)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,  # Set to False for development without HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return response

@router.get("/login")
async def login_page(request: Request, next: Optional[str] = None):
    """Display login page"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next}
    )

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    user: User = Depends(get_current_user)
):
    """User logout"""
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_id")
    return response

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(str(current_user.id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_service = UserService(db)
    user = user_service.update_user(str(current_user.id), user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Change user password"""
    user_service = UserService(db)
    success = user_service.change_password(str(current_user.id), password_data)
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )

@router.get("/dashboard")
async def dashboard(
    request: Request,
    current_user: User = Depends(require_auth)
):
    """User dashboard"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": current_user}
    )