from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    language_preference: str = Field(default="en", regex="^(en|fr|ar)$")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    tier: UserTier = UserTier.FREE
    status: UserStatus = UserStatus.ACTIVE
    language_preference: str = "en"
    newsletter_frequency: str = "weekly"
    preferences: Dict[str, Any] = {}
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    language_preference: Optional[str] = Field(None, regex="^(en|fr|ar)$")
    newsletter_frequency: Optional[str] = Field(None, regex="^(daily|weekly|monthly)$")
    preferences: Optional[Dict[str, Any]] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class EmailVerification(BaseModel):
    token: str

class AuthResponse(BaseModel):
    user: UserProfile
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthStatus(BaseModel):
    is_authenticated: bool
    user: Optional[UserProfile] = None
    message: Optional[str] = None 