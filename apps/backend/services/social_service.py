"""
Social Features Service
Handles user follows, shared watchlists, leaderboards, and social activities
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models.user import User, UserProfile
from models.social import (
    UserFollow, SharedWatchlist, SharedWatchlistItem, 
    Leaderboard, SocialActivity
)

logger = logging.getLogger(__name__)


class SocialService:
    """Service for social features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # USER FOLLOWS
    # ============================================================================
    
    async def follow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        """Follow another user"""
        try:
            # Check if already following
            existing_follow = self.db.query(UserFollow).filter(
                and_(
                    UserFollow.follower_id == follower_id,
                    UserFollow.following_id == following_id
                )
            ).first()
            
            if existing_follow:
                raise HTTPException(status_code=400, detail="Already following this user")
            
            # Create follow relationship
            follow = UserFollow(
                follower_id=follower_id,
                following_id=following_id
            )
            self.db.add(follow)
            self.db.commit()
            
            # Create social activity
            activity = SocialActivity(
                user_id=follower_id,
                activity_type="follow_user",
                target_id=following_id,
                target_type="user",
                content=f"Started following a user"
            )
            self.db.add(activity)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Successfully followed user",
                "follow_id": str(follow.id)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error following user: {e}")
            raise HTTPException(status_code=500, detail="Failed to follow user")
    
    async def unfollow_user(self, follower_id: str, following_id: str) -> Dict[str, Any]:
        """Unfollow a user"""
        try:
            follow = self.db.query(UserFollow).filter(
                and_(
                    UserFollow.follower_id == follower_id,
                    UserFollow.following_id == following_id
                )
            ).first()
            
            if not follow:
                raise HTTPException(status_code=404, detail="Follow relationship not found")
            
            self.db.delete(follow)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Successfully unfollowed user"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unfollowing user: {e}")
            raise HTTPException(status_code=500, detail="Failed to unfollow user")
    
    async def get_followers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of followers for a user"""
        try:
            followers = self.db.query(UserFollow).filter(
                UserFollow.following_id == user_id
            ).all()
            
            follower_data = []
            for follow in followers:
                user = self.db.query(User).filter(User.id == follow.follower_id).first()
                if user:
                    follower_data.append({
                        "user_id": str(user.id),
                        "email": user.email,
                        "followed_at": follow.created_at.isoformat()
                    })
            
            return follower_data
            
        except Exception as e:
            logger.error(f"Error getting followers: {e}")
            raise HTTPException(status_code=500, detail="Failed to get followers")
    
    async def get_following(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of users being followed"""
        try:
            following = self.db.query(UserFollow).filter(
                UserFollow.follower_id == user_id
            ).all()
            
            following_data = []
            for follow in following:
                user = self.db.query(User).filter(User.id == follow.following_id).first()
                if user:
                    following_data.append({
                        "user_id": str(user.id),
                        "email": user.email,
                        "followed_at": follow.created_at.isoformat()
                    })
            
            return following_data
            
        except Exception as e:
            logger.error(f"Error getting following: {e}")
            raise HTTPException(status_code=500, detail="Failed to get following")
    
    # ============================================================================
    # SHARED WATCHLISTS
    # ============================================================================
    
    async def create_shared_watchlist(
        self, 
        user_id: str, 
        name: str, 
        description: Optional[str] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """Create a shared watchlist"""
        try:
            watchlist = SharedWatchlist(
                user_id=user_id,
                name=name,
                description=description,
                is_public=is_public
            )
            self.db.add(watchlist)
            self.db.commit()
            
            # Create social activity
            activity = SocialActivity(
                user_id=user_id,
                activity_type="watchlist_created",
                target_id=watchlist.id,
                target_type="shared_watchlist",
                content=f"Created shared watchlist: {name}"
            )
            self.db.add(activity)
            self.db.commit()
            
            return {
                "success": True,
                "watchlist_id": str(watchlist.id),
                "name": watchlist.name,
                "message": "Watchlist created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating shared watchlist: {e}")
            raise HTTPException(status_code=500, detail="Failed to create watchlist")
    
    async def add_to_shared_watchlist(
        self, 
        watchlist_id: str, 
        ticker: str, 
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a ticker to a shared watchlist"""
        try:
            # Check if ticker already exists
            existing_item = self.db.query(SharedWatchlistItem).filter(
                and_(
                    SharedWatchlistItem.watchlist_id == watchlist_id,
                    SharedWatchlistItem.ticker == ticker
                )
            ).first()
            
            if existing_item:
                raise HTTPException(status_code=400, detail="Ticker already in watchlist")
            
            item = SharedWatchlistItem(
                watchlist_id=watchlist_id,
                ticker=ticker,
                notes=notes
            )
            self.db.add(item)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Added {ticker} to watchlist"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding to shared watchlist: {e}")
            raise HTTPException(status_code=500, detail="Failed to add to watchlist")
    
    async def get_public_watchlists(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get public watchlists"""
        try:
            watchlists = self.db.query(SharedWatchlist).filter(
                SharedWatchlist.is_public == True
            ).order_by(desc(SharedWatchlist.follower_count)).limit(limit).all()
            
            watchlist_data = []
            for watchlist in watchlists:
                # Get creator info
                creator = self.db.query(User).filter(User.id == watchlist.user_id).first()
                
                # Get item count
                item_count = self.db.query(SharedWatchlistItem).filter(
                    SharedWatchlistItem.watchlist_id == watchlist.id
                ).count()
                
                watchlist_data.append({
                    "id": str(watchlist.id),
                    "name": watchlist.name,
                    "description": watchlist.description,
                    "creator_email": creator.email if creator else "Unknown",
                    "follower_count": watchlist.follower_count,
                    "item_count": item_count,
                    "created_at": watchlist.created_at.isoformat()
                })
            
            return watchlist_data
            
        except Exception as e:
            logger.error(f"Error getting public watchlists: {e}")
            raise HTTPException(status_code=500, detail="Failed to get public watchlists")
    
    async def get_watchlist_items(self, watchlist_id: str) -> List[Dict[str, Any]]:
        """Get items in a shared watchlist"""
        try:
            items = self.db.query(SharedWatchlistItem).filter(
                SharedWatchlistItem.watchlist_id == watchlist_id
            ).all()
            
            item_data = []
            for item in items:
                item_data.append({
                    "ticker": item.ticker,
                    "notes": item.notes,
                    "added_at": item.added_at.isoformat()
                })
            
            return item_data
            
        except Exception as e:
            logger.error(f"Error getting watchlist items: {e}")
            raise HTTPException(status_code=500, detail="Failed to get watchlist items")
    
    # ============================================================================
    # LEADERBOARDS
    # ============================================================================
    
    async def update_leaderboard_score(
        self,
        user_id: str,
        leaderboard_type: str,
        score: Decimal,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """Update a user's leaderboard score"""
        try:
            # Get current period dates
            now = datetime.now()
            if period == "daily":
                period_start = now.date()
                period_end = now.date()
            elif period == "weekly":
                period_start = (now - timedelta(days=now.weekday())).date()
                period_end = (period_start + timedelta(days=6))
            elif period == "monthly":
                period_start = now.replace(day=1).date()
                period_end = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            else:  # yearly
                period_start = now.replace(month=1, day=1).date()
                period_end = now.replace(month=12, day=31).date()
            
            # Update or create leaderboard entry
            existing_entry = self.db.query(Leaderboard).filter(
                and_(
                    Leaderboard.user_id == user_id,
                    Leaderboard.leaderboard_type == leaderboard_type,
                    Leaderboard.period == period,
                    Leaderboard.period_start == period_start
                )
            ).first()
            
            if existing_entry:
                existing_entry.score = score
                existing_entry.updated_at = now
            else:
                entry = Leaderboard(
                    user_id=user_id,
                    leaderboard_type=leaderboard_type,
                    score=score,
                    period=period,
                    period_start=period_start,
                    period_end=period_end
                )
                self.db.add(entry)
            
            self.db.commit()
            
            # Update rankings
            await self._update_leaderboard_rankings(leaderboard_type, period, period_start)
            
            return {
                "success": True,
                "message": "Leaderboard score updated"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating leaderboard score: {e}")
            raise HTTPException(status_code=500, detail="Failed to update leaderboard score")
    
    async def _update_leaderboard_rankings(
        self, 
        leaderboard_type: str, 
        period: str, 
        period_start: datetime.date
    ):
        """Update rankings for a leaderboard"""
        try:
            # Get all entries for this leaderboard
            entries = self.db.query(Leaderboard).filter(
                and_(
                    Leaderboard.leaderboard_type == leaderboard_type,
                    Leaderboard.period == period,
                    Leaderboard.period_start == period_start
                )
            ).order_by(desc(Leaderboard.score)).all()
            
            # Update rankings
            for rank, entry in enumerate(entries, 1):
                entry.rank = rank
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating leaderboard rankings: {e}")
    
    async def get_leaderboard(
        self, 
        leaderboard_type: str, 
        period: str = "daily", 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get leaderboard rankings"""
        try:
            # Get current period
            now = datetime.now()
            if period == "daily":
                period_start = now.date()
            elif period == "weekly":
                period_start = (now - timedelta(days=now.weekday())).date()
            elif period == "monthly":
                period_start = now.replace(day=1).date()
            else:  # yearly
                period_start = now.replace(month=1, day=1).date()
            
            entries = self.db.query(Leaderboard).filter(
                and_(
                    Leaderboard.leaderboard_type == leaderboard_type,
                    Leaderboard.period == period,
                    Leaderboard.period_start == period_start
                )
            ).order_by(Leaderboard.rank).limit(limit).all()
            
            leaderboard_data = []
            for entry in entries:
                user = self.db.query(User).filter(User.id == entry.user_id).first()
                leaderboard_data.append({
                    "rank": entry.rank,
                    "user_id": str(entry.user_id),
                    "user_email": user.email if user else "Unknown",
                    "score": float(entry.score),
                    "period": entry.period
                })
            
            return leaderboard_data
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            raise HTTPException(status_code=500, detail="Failed to get leaderboard")
    
    # ============================================================================
    # SOCIAL ACTIVITY FEED
    # ============================================================================
    
    async def get_social_feed(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get social activity feed for a user"""
        try:
            # Get activities from followed users and public activities
            activities = self.db.query(SocialActivity).filter(
                and_(
                    SocialActivity.is_public == True,
                    SocialActivity.user_id != user_id
                )
            ).order_by(desc(SocialActivity.created_at)).limit(limit).all()
            
            activity_data = []
            for activity in activities:
                user = self.db.query(User).filter(User.id == activity.user_id).first()
                activity_data.append({
                    "id": str(activity.id),
                    "user_id": str(activity.user_id),
                    "user_email": user.email if user else "Unknown",
                    "activity_type": activity.activity_type,
                    "content": activity.content,
                    "target_id": str(activity.target_id) if activity.target_id else None,
                    "target_type": activity.target_type,
                    "created_at": activity.created_at.isoformat()
                })
            
            return activity_data
            
        except Exception as e:
            logger.error(f"Error getting social feed: {e}")
            raise HTTPException(status_code=500, detail="Failed to get social feed")
    
    async def create_social_activity(
        self,
        user_id: str,
        activity_type: str,
        content: str,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        is_public: bool = True
    ) -> Dict[str, Any]:
        """Create a social activity"""
        try:
            activity = SocialActivity(
                user_id=user_id,
                activity_type=activity_type,
                content=content,
                target_id=target_id,
                target_type=target_type,
                is_public=is_public
            )
            self.db.add(activity)
            self.db.commit()
            
            return {
                "success": True,
                "activity_id": str(activity.id),
                "message": "Activity created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating social activity: {e}")
            raise HTTPException(status_code=500, detail="Failed to create activity") 