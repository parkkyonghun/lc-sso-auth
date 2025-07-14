import os
import uuid
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import FastAPI, Request, Depends, Form, HTTPException, status, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON as SAJSON
from sqlalchemy.orm import relationship
from jose import jwt

import os
from app.core.config import settings
from app.core.security import create_jwt, decode_jwt, hash_password, verify_password
from app.core.auth import get_current_user, get_current_admin_user
from app.services.user_service import UserService
from app.services.application_service import ApplicationService
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin
from app.schemas.application import ApplicationCreate
from app.database import get_db, Base, engine
from app.models.user import User
from app.models.application import Application

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")



app = FastAPI() 

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    full_name: str = Form(None),
    db=Depends(get_db)
):
    user_service = UserService(db)
    if user_service.get_user_by_username(username):
        raise HTTPException(status_code=400, detail="Username exists")
    user_data = UserCreate(
        username=username,
        password=password,
        email=email,
        full_name=full_name,
    )
    user_service.create_user(user_data)
    return {"msg": "registered"}

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    sid = auth_service.create_session(user.id)
    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie("session", sid, httponly=True)
    return resp

@app.get("/logout")
async def logout(request: Request):
    auth_service = AuthService(None) # No DB needed for session deletion
    sid = request.cookies.get("session")
    if sid:
        auth_service.delete_session(sid)
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("session")
    return resp

@app.post("/applications")
async def register_app(
    name: str = Form(...),
    redirect_uris: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    db=Depends(get_db),
    request: Request = None
):
    auth_service = AuthService(db)
    application_service = ApplicationService(db)
    owner_id = None
    sid = request.cookies.get("session") if request else None
    if sid:
        owner_id = auth_service.get_session(sid)
    if not owner_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if application_service.get_application_by_client_id(client_id):
        raise HTTPException(status_code=400, detail="Client ID exists")
    app_data = ApplicationCreate(
        name=name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uris=json.loads(redirect_uris),
        owner_id=owner_id,
    )
    application_service.create_application(app_data)
    return {"msg": "application registered"}

@app.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str = "",
    state: str = "",
    request: Request,
    db=Depends(get_db)
):
    auth_service = AuthService(db)
    application_service = ApplicationService(db)
    sid = request.cookies.get("session")
    user_id = auth_service.get_session(sid) if sid else None
    app_obj = application_service.get_application_by_client_id(client_id)
    if not app_obj or redirect_uri not in app_obj.redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid client or redirect_uri")
    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request, "client_id": client_id, "redirect_uri": redirect_uri, "state": state})
    # Consent page could be shown here, but for minimal version, auto-consent
    code = auth_service.create_auth_code(user_id, client_id, redirect_uri)
    url = f"{redirect_uri}?code={code}&state={state}"
    return RedirectResponse(url=url, status_code=302)
    
@app.get("/consent")
async def consent(
    request: Request,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    db=Depends(get_db)
):
    auth_service = AuthService(db)
    application_service = ApplicationService(db)
    sid = request.cookies.get("session")
    user_id = auth_service.get_session(sid) if sid else None
    app_obj = application_service.get_application_by_client_id(client_id)
    if not app_obj or redirect_uri not in app_obj.redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid client or redirect_uri")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.post("/token")
async def token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    db=Depends(get_db)
):
    auth_service = AuthService(db)
    if grant_type == "authorization_code":
        auth_data = auth_service.consume_auth_code(code)
        if not auth_data or auth_data["client_id"] != client_id or auth_data["redirect_uri"] != redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        user_id = auth_data["user_id"]
        access_token = auth_service.create_access_token(data={"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    elif grant_type == "refresh_token":
        try:
            payload = auth_service.decode_jwt(refresh_token)
            user_id = payload["sub"]
            access_token = auth_service.create_access_token(data={"sub": user_id})
            return {"access_token": access_token, "token_type": "bearer"}
        except:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    raise HTTPException(status_code=400, detail="Unsupported grant type")

@app.get("/userinfo")
async def userinfo(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), db=Depends(get_db)):
    auth_service = AuthService(db)
    user_service = UserService(db)
    try:
        payload = auth_service.decode_jwt(token)
        user_id = payload["sub"]
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"sub": user.id, "email": user.email, "name": user.full_name}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/.well-known/jwks.json")
async def jwks():
    auth_service = AuthService(None) # No DB needed for public key
    public_key_pem = auth_service.get_public_key()
    # Parse the PEM formatted public key to extract n and e
    # This is a simplified example, a real implementation would use a proper JWK library
    # For now, we'll just return a dummy JWK with the actual public key content
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "1", # Key ID
                "alg": settings.jwt_algorithm,
                "n": public_key_pem, # In a real scenario, this would be the base64url encoded modulus
                "e": "AQAB" # Base64url encoded public exponent
            }
        ]
    }

@app.get("/.well-known/openid-configuration")
async def oidc_config(request: Request):
    host = request.url.scheme + "://" + request.url.hostname
    return {
        "issuer": host,
        "authorization_endpoint": host + "/authorize",
        "token_endpoint": host + "/token",
        "userinfo_endpoint": host + "/userinfo",
        "jwks_uri": host + "/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": [settings.jwt_algorithm],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
    }