import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status
import secrets
import string
import hashlib
from .config import settings
from .cache import get_cache

# Password hashing using SHA256
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
cache = get_cache()

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(password, hashed)

def create_jwt(payload: Dict[str, Any], exp_min: int = None) -> str:
    """Create a JWT token with the given payload"""
    if exp_min is None:
        exp_min = settings.jwt_access_token_expire_minutes
    
    to_encode = payload.copy()
    now = datetime.utcnow()
    to_encode.update({
        "exp": now + timedelta(minutes=exp_min),
        "iat": now,
        "iss": settings.app_name
    })
    
    return jwt.encode(to_encode, settings.jwt_private_key, algorithm=settings.jwt_algorithm)

def decode_jwt(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_public_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_access_token(user_id: str, scope: str = "openid profile email") -> str:
    """Create an access token for a user"""
    payload = {
        "sub": user_id,
        "scope": scope,
        "token_type": "access_token"
    }
    return create_jwt(payload)

def create_id_token(user_data: Dict[str, Any]) -> str:
    """Create an ID token with user information"""
    payload = {
        "sub": user_data["id"],
        "email": user_data.get("email"),
        "name": user_data.get("full_name"),
        "username": user_data.get("username"),
        "token_type": "id_token"
    }
    return create_jwt(payload)

def create_session(user_id: str) -> str:
    """Create a user session and store it in cache"""
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store session for 24 hours
    cache.setex(f"session:{session_id}", 86400, json.dumps(session_data))
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data from cache"""
    if not session_id:
        return None
    
    session_data = cache.get(f"session:{session_id}")
    if session_data:
        try:
            return json.loads(session_data)
        except json.JSONDecodeError:
            return None
    return None

def delete_session(session_id: str) -> bool:
    """Delete a session from cache"""
    return cache.delete(f"session:{session_id}")

def create_auth_code(user_id: str, client_id: str, redirect_uri: str, scope: str = "") -> str:
    """Create an authorization code for OAuth flow"""
    code = str(uuid.uuid4())
    code_data = {
        "user_id": user_id,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store authorization code for 10 minutes
    cache.setex(f"auth_code:{code}", 600, json.dumps(code_data))
    return code

def consume_auth_code(code: str) -> Optional[Dict[str, Any]]:
    """Consume an authorization code (one-time use)"""
    if not code:
        return None
    
    code_data = cache.get(f"auth_code:{code}")
    if code_data:
        # Delete the code immediately to ensure one-time use
        cache.delete(f"auth_code:{code}")
        try:
            return json.loads(code_data)
        except json.JSONDecodeError:
            return None
    return None

def validate_redirect_uri(redirect_uri: str, allowed_uris: list) -> bool:
    """Validate if redirect URI is in the allowed list"""
    return redirect_uri in allowed_uris

def generate_client_credentials() -> tuple[str, str]:
    """Generate client ID and client secret"""
    client_id = f"client_{uuid.uuid4().hex[:16]}"
    client_secret = uuid.uuid4().hex
    return client_id, client_secret

def create_rate_limit_key(identifier: str, endpoint: str) -> str:
    """Create a rate limit key for caching"""
    return f"rate_limit:{identifier}:{endpoint}"

def check_rate_limit(identifier: str, endpoint: str, limit: int = 60, window: int = 60) -> bool:
    """Check if request is within rate limit"""
    key = create_rate_limit_key(identifier, endpoint)
    current = cache.get(key)
    
    if current is None:
        cache.setex(key, window, "1")
        return True
    
    try:
        count = int(current)
        if count >= limit:
            return False
        
        # Increment counter
        cache.set(key, str(count + 1), ex=window)
        return True
    except (ValueError, TypeError):
        return False