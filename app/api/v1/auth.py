from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from ...models.user import User
from ...core.database import get_db
from ...core.security import (
    create_session, get_session, delete_session, decode_jwt, check_rate_limit,
    create_access_token, create_refresh_token, blacklist_token, is_token_blacklisted,
    store_refresh_token, get_refresh_token, revoke_refresh_token, revoke_all_user_tokens
)
from ...schemas.user import UserCreate, UserResponse, UserUpdate, PasswordChange
from ...services.user_service import UserService

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
    import time
    login_start = time.time()
    
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip, "login", limit=20, window=900):  # 20 attempts per 15 minutes
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
        # Create both access and refresh tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        # Store refresh token (extract JTI from token)
        try:
            refresh_payload = decode_jwt(refresh_token)
            refresh_jti = refresh_payload.get("jti")
            if refresh_jti:
                store_refresh_token(str(user.id), refresh_token, refresh_jti)
        except Exception as e:
            # If token storage fails, continue without refresh token
            pass
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer", 
            "expires_in": 3600,  # 1 hour
            "user": {
                "id": str(user.id), 
                "username": user.username, 
                "email": user.email, 
                "full_name": user.full_name,
                "is_superuser": user.is_superuser
            }
        }
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
    
    # Log login performance
    login_duration = time.time() - login_start
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login completed for user {username} in {login_duration:.3f}s")
    
    return response

@router.get("/login")
async def login_page(request: Request, next: Optional[str] = None):
    """Display login page"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next}
    )

@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        data = await request.json()
        refresh_token = data.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Validate refresh token
        try:
            payload = decode_jwt(refresh_token)
            if payload.get("token_type") != "refresh_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            refresh_jti = payload.get("jti")
            
            if not user_id or not refresh_jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Check if refresh token exists in cache
            stored_token = get_refresh_token(refresh_jti)
            if not stored_token or stored_token.get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )
            
            # Get user
            user_service = UserService(db)
            user = user_service.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Create new access token
            new_access_token = create_access_token(user_id)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": 3600,  # 1 hour
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_superuser": user.is_superuser
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request format"
        )

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: User = Depends(get_current_user)
):
    """User logout"""
    # Handle session-based logout
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    
    # Handle token-based logout
    if credentials:
        try:
            payload = decode_jwt(credentials.credentials)
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                # Calculate remaining time to expiry
                import time
                remaining_time = exp - int(time.time())
                if remaining_time > 0:
                    blacklist_token(jti, remaining_time)
            
            # If user is provided, also revoke refresh tokens
            if user:
                revoke_all_user_tokens(str(user.id))
        except Exception:
            pass  # Ignore token errors during logout
    
    # Check if it's an API request
    accept_header = request.headers.get("accept", "")
    x_requested_with = request.headers.get("x-requested-with", "")
    is_api_client = accept_header.lower() == "application/json" or x_requested_with.lower() == "xmlhttprequest"
    
    if is_api_client:
        return {"message": "Logged out successfully"}
    
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