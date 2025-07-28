from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime

from models.user import (
    UserRegistration, UserLogin, UserProfile, UserProfileUpdate,
    PasswordResetRequest, PasswordReset, EmailVerification,
    AuthResponse, TokenResponse, AuthStatus
)
from services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return await auth_service.get_current_user(token)

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """Login a user"""
    return await auth_service.login_user(login_data)

@router.post("/logout")
async def logout_user(current_user: UserProfile = Depends(get_current_user)):
    """Logout a user"""
    return await auth_service.logout_user(current_user.id)

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update current user profile"""
    return await auth_service.update_user_profile(current_user.id, profile_data)

@router.post("/password/reset-request")
async def request_password_reset(reset_data: PasswordResetRequest):
    """Request password reset email"""
    return await auth_service.request_password_reset(reset_data)

@router.post("/password/reset")
async def reset_password(reset_data: PasswordReset):
    """Reset password with token"""
    return await auth_service.reset_password(reset_data)

@router.post("/email/verify")
async def verify_email(verification_data: EmailVerification):
    """Verify email with token"""
    return await auth_service.verify_email(verification_data)

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    return await auth_service.refresh_token(refresh_token)

@router.get("/status", response_model=AuthStatus)
async def check_auth_status(authorization: Optional[str] = Header(None)):
    """Check authentication status"""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    
    return await auth_service.check_auth_status(token)

@router.get("/")
async def get_auth():
    """Get auth functionality info"""
    return {
        "message": "Authentication endpoints available",
        "endpoints": [
            "POST /register - Register new user",
            "POST /login - Login user",
            "POST /logout - Logout user",
            "GET /profile - Get user profile",
            "PUT /profile - Update user profile",
            "POST /password/reset-request - Request password reset",
            "POST /password/reset - Reset password",
            "POST /email/verify - Verify email",
            "POST /token/refresh - Refresh access token",
            "GET /status - Check auth status"
        ]
    } 