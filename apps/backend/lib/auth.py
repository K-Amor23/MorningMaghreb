"""
Simple authentication module for testing purposes
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

security = HTTPBearer()

class User(BaseModel):
    id: str
    email: str
    name: str = "Test User"

# Mock user for testing
MOCK_USER = User(
    id="00000000-0000-0000-0000-000000000001",
    email="test@example.com",
    name="Test User"
)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """
    Mock authentication function for testing
    In production, this would validate the JWT token
    """
    # For testing, return mock user
    # In production, you would:
    # 1. Validate the JWT token
    # 2. Extract user info from token
    # 3. Return user object
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock validation - in production, validate the token
    if credentials.credentials == "test-token":
        return MOCK_USER
    
    # For development/testing, return mock user for any token
    return MOCK_USER

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Mock function for testing without authentication
async def get_mock_user() -> User:
    """Mock user for testing endpoints without authentication"""
    return MOCK_USER 