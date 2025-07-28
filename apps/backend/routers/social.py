"""
Social Features Router
Handles user follows, shared watchlists, leaderboards, and social activities
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from database.connection import get_db
from services.social_service import SocialService
from utils.auth import get_current_user

router = APIRouter()
security = HTTPBearer()

# ============================================================================
# USER FOLLOWS
# ============================================================================

@router.post("/follow/{user_id}")
async def follow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow another user"""
    social_service = SocialService(db)
    return await social_service.follow_user(current_user["id"], user_id)

@router.delete("/unfollow/{user_id}")
async def unfollow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    social_service = SocialService(db)
    return await social_service.unfollow_user(current_user["id"], user_id)

@router.get("/followers")
async def get_followers(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of followers"""
    social_service = SocialService(db)
    return await social_service.get_followers(current_user["id"])

@router.get("/following")
async def get_following(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users being followed"""
    social_service = SocialService(db)
    return await social_service.get_following(current_user["id"])

# ============================================================================
# SHARED WATCHLISTS
# ============================================================================

@router.post("/watchlists")
async def create_shared_watchlist(
    name: str,
    description: Optional[str] = None,
    is_public: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shared watchlist"""
    social_service = SocialService(db)
    return await social_service.create_shared_watchlist(
        current_user["id"], name, description, is_public
    )

@router.post("/watchlists/{watchlist_id}/items")
async def add_to_shared_watchlist(
    watchlist_id: str,
    ticker: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a ticker to a shared watchlist"""
    social_service = SocialService(db)
    return await social_service.add_to_shared_watchlist(
        watchlist_id, ticker, notes
    )

@router.get("/watchlists/public")
async def get_public_watchlists(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get public watchlists"""
    social_service = SocialService(db)
    return await social_service.get_public_watchlists(limit)

@router.get("/watchlists/{watchlist_id}/items")
async def get_watchlist_items(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Get items in a shared watchlist"""
    social_service = SocialService(db)
    return await social_service.get_watchlist_items(watchlist_id)

# ============================================================================
# LEADERBOARDS
# ============================================================================

@router.post("/leaderboards/update")
async def update_leaderboard_score(
    leaderboard_type: str,
    score: float,
    period: str = "daily",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user's leaderboard score"""
    from decimal import Decimal
    social_service = SocialService(db)
    return await social_service.update_leaderboard_score(
        current_user["id"], leaderboard_type, Decimal(str(score)), period
    )

@router.get("/leaderboards/{leaderboard_type}")
async def get_leaderboard(
    leaderboard_type: str,
    period: str = "daily",
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get leaderboard rankings"""
    social_service = SocialService(db)
    return await social_service.get_leaderboard(leaderboard_type, period, limit)

# ============================================================================
# SOCIAL ACTIVITY FEED
# ============================================================================

@router.get("/feed")
async def get_social_feed(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social activity feed"""
    social_service = SocialService(db)
    return await social_service.get_social_feed(current_user["id"], limit)

@router.post("/activities")
async def create_social_activity(
    activity_type: str,
    content: str,
    target_id: Optional[str] = None,
    target_type: Optional[str] = None,
    is_public: bool = True,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a social activity"""
    social_service = SocialService(db)
    return await social_service.create_social_activity(
        current_user["id"], activity_type, content, target_id, target_type, is_public
    ) 