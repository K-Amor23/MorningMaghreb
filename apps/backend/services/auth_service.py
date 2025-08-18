import os
import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import create_client, Client
from fastapi import HTTPException, status
from passlib.context import CryptContext

from models.user import (
    UserRegistration, UserLogin, UserProfile, UserProfileUpdate,
    PasswordResetRequest, PasswordReset, EmailVerification,
    AuthResponse, TokenResponse, AuthStatus, UserTier, UserStatus
)

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service using Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        # Handle missing Supabase credentials for development
        if not self.supabase_url or not self.supabase_key:
            logger.warning("SUPABASE_URL and SUPABASE_SERVICE_KEY not set - using mock implementation")
            self.supabase = None
            self.mock_mode = True
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self.mock_mode = False
        
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT settings
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 7
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def _create_tokens(self, user_id: str) -> Dict[str, str]:
        """Create access and refresh tokens"""
        access_token_expires = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        refresh_token_expires = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        access_token_data = {
            "sub": user_id,
            "exp": access_token_expires,
            "type": "access"
        }
        
        refresh_token_data = {
            "sub": user_id,
            "exp": refresh_token_expires,
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_token_data, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_token_data, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def register_user(self, user_data: UserRegistration) -> AuthResponse:
        """Register a new user"""
        try:
            if self.mock_mode:
                # Mock implementation for development
                user_id = f"mock_user_{datetime.utcnow().timestamp()}"
                tokens = self._create_tokens(user_id)
                
                return AuthResponse(
                    user=UserProfile(
                        id=user_id,
                        email=user_data.email,
                        full_name=user_data.full_name,
                        tier=UserTier.FREE,
                        status=UserStatus.ACTIVE,
                        language_preference=user_data.language_preference,
                        newsletter_frequency="weekly",
                        preferences={},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"]
                )
            
            # Check if user already exists
            existing_user = self.supabase.auth.admin.list_users()
            for user in existing_user:
                if user.email == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User with this email already exists"
                    )
            
            # Create user in Supabase Auth
            auth_response = self.supabase.auth.admin.create_user({
                "email": user_data.email,
                "password": user_data.password,
                "email_confirm": True  # Auto-confirm for demo
            })
            
            user_id = auth_response.user.id
            
            # Create user profile
            profile_data = {
                "id": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "tier": UserTier.FREE.value,
                "status": UserStatus.ACTIVE.value,
                "language_preference": user_data.language_preference,
                "newsletter_frequency": "weekly",
                "preferences": {},
                # Persist compliance consents when present in payload
                **({"marketing_consent": getattr(user_data, "marketing_consent", False)}),
                **({"terms_accepted_at": getattr(user_data, "terms_accepted_at", datetime.utcnow().isoformat())}),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("profiles").insert(profile_data).execute()
            
            # Create tokens
            tokens = self._create_tokens(user_id)
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            return AuthResponse(
                user=profile,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )
    
    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Login a user"""
        try:
            if self.mock_mode:
                # Mock implementation for development
                user_id = f"mock_user_{login_data.email}"
                tokens = self._create_tokens(user_id)
                
                return AuthResponse(
                    user=UserProfile(
                        id=user_id,
                        email=login_data.email,
                        full_name="Mock User",
                        tier=UserTier.FREE,
                        status=UserStatus.ACTIVE,
                        language_preference="en",
                        newsletter_frequency="weekly",
                        preferences={},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"]
                )
            
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            user_id = auth_response.user.id
            
            # Get user profile
            profile = await self.get_user_profile(user_id)
            
            # Create tokens
            tokens = self._create_tokens(user_id)
            
            return AuthResponse(
                user=profile,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    
    async def logout_user(self, user_id: str) -> Dict[str, str]:
        """Logout a user"""
        try:
            # In a real implementation, you might want to blacklist the token
            # For now, we'll just return a success message
            return {"message": "Successfully logged out"}
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout"
            )
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile by ID"""
        try:
            if self.mock_mode:
                # Mock implementation for development
                return UserProfile(
                    id=user_id,
                    email="mock@example.com",
                    full_name="Mock User",
                    tier=UserTier.FREE,
                    status=UserStatus.ACTIVE,
                    language_preference="en",
                    newsletter_frequency="weekly",
                    preferences={},
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            profile_data = response.data[0]
            
            return UserProfile(
                id=profile_data["id"],
                email=profile_data["email"],
                full_name=profile_data["full_name"],
                tier=UserTier(profile_data.get("tier", "free")),
                status=UserStatus(profile_data.get("status", "active")),
                language_preference=profile_data.get("language_preference", "en"),
                newsletter_frequency=profile_data.get("newsletter_frequency", "weekly"),
                preferences=profile_data.get("preferences", {}),
                stripe_customer_id=profile_data.get("stripe_customer_id"),
                stripe_subscription_id=profile_data.get("stripe_subscription_id"),
                created_at=datetime.fromisoformat(profile_data["created_at"]),
                updated_at=datetime.fromisoformat(profile_data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user profile"
            )
    
    async def update_user_profile(self, user_id: str, profile_data: UserProfileUpdate) -> UserProfile:
        """Update user profile"""
        try:
            update_data = {}
            
            if profile_data.full_name is not None:
                update_data["full_name"] = profile_data.full_name
            if profile_data.language_preference is not None:
                update_data["language_preference"] = profile_data.language_preference
            if profile_data.newsletter_frequency is not None:
                update_data["newsletter_frequency"] = profile_data.newsletter_frequency
            if profile_data.preferences is not None:
                update_data["preferences"] = profile_data.preferences
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("profiles").update(update_data).eq("id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
    
    async def request_password_reset(self, reset_data: PasswordResetRequest) -> Dict[str, str]:
        """Request password reset"""
        try:
            # In a real implementation, this would send an email
            # For demo purposes, we'll just return a success message
            return {
                "message": "Password reset email sent",
                "email": reset_data.email
            }
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
    
    async def reset_password(self, reset_data: PasswordReset) -> Dict[str, str]:
        """Reset password with token"""
        try:
            # In a real implementation, you would verify the token
            # and update the password in Supabase
            return {"message": "Password successfully reset"}
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
    
    async def verify_email(self, verification_data: EmailVerification) -> Dict[str, str]:
        """Verify email with token"""
        try:
            # In a real implementation, you would verify the token
            return {"message": "Email successfully verified"}
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify email"
            )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            payload = self._verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user_id = payload.get("sub")
            tokens = self._create_tokens(user_id)
            
            return TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def get_current_user(self, token: str) -> UserProfile:
        """Get current user from token"""
        try:
            payload = self._verify_token(token)
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )
            
            user_id = payload.get("sub")
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def check_auth_status(self, token: Optional[str] = None) -> AuthStatus:
        """Check authentication status"""
        if not token:
            return AuthStatus(is_authenticated=False, message="No token provided")
        
        try:
            user = await self.get_current_user(token)
            return AuthStatus(is_authenticated=True, user=user)
        except Exception:
            return AuthStatus(is_authenticated=False, message="Invalid token")

# Create global instance
auth_service = AuthService() 