from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from enum import Enum

from pydantic import BaseModel
from utils.auth import get_current_user

router = APIRouter(prefix="/social-trading", tags=["Social Trading"])

# Social Trading Models
class ShareSettings(BaseModel):
    is_public: bool = False
    share_positions: bool = False
    share_performance: bool = True
    display_name: str
    description: Optional[str] = None

class SocialPortfolio(BaseModel):
    id: str
    account_id: str
    user_id: str
    display_name: str
    description: Optional[str] = None
    is_public: bool = False
    share_positions: bool = False
    share_performance: bool = True
    follower_count: int = 0
    total_return_percent: Decimal
    created_at: datetime
    updated_at: datetime

class SocialActivity(BaseModel):
    id: str
    user_id: str
    account_id: str
    activity_type: str  # 'trade', 'milestone', 'share', 'follow'
    content: Dict[str, Any]
    created_at: datetime

class CompetitionInfo(BaseModel):
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    entry_fee: Decimal
    prize_pool: Decimal
    participant_count: int
    is_active: bool
    rules: Dict[str, Any]

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    display_name: str
    account_id: str
    total_return: Decimal
    total_return_percent: Decimal
    sharpe_ratio: Optional[Decimal] = None
    max_drawdown: Optional[Decimal] = None
    trades_count: int

class SocialFeedItem(BaseModel):
    id: str
    user_display_name: str
    activity_type: str
    content: Dict[str, Any]
    created_at: datetime

# Mock data storage
mock_social_portfolios = {}
mock_social_activities = {}
mock_competitions = {}
mock_leaderboards = {}
mock_follows = {}

@router.post("/portfolios/{account_id}/share", response_model=SocialPortfolio)
async def share_portfolio(
    account_id: str,
    share_settings: ShareSettings,
    current_user = Depends(get_current_user)
):
    """Share a paper trading portfolio with the community"""
    portfolio_id = str(uuid.uuid4())
    
    # Check if portfolio already exists
    existing_portfolio = None
    for portfolio in mock_social_portfolios.values():
        if portfolio.account_id == account_id and portfolio.user_id == current_user.id:
            existing_portfolio = portfolio
            break
    
    if existing_portfolio:
        # Update existing portfolio
        existing_portfolio.display_name = share_settings.display_name
        existing_portfolio.description = share_settings.description
        existing_portfolio.is_public = share_settings.is_public
        existing_portfolio.share_positions = share_settings.share_positions
        existing_portfolio.share_performance = share_settings.share_performance
        existing_portfolio.updated_at = datetime.now()
        
        # Create activity
        activity_id = str(uuid.uuid4())
        activity = SocialActivity(
            id=activity_id,
            user_id=current_user.id,
            account_id=account_id,
            activity_type="share",
            content={
                "action": "updated_portfolio",
                "portfolio_name": share_settings.display_name,
                "is_public": share_settings.is_public
            },
            created_at=datetime.now()
        )
        mock_social_activities[activity_id] = activity
        
        return existing_portfolio
    else:
        # Create new shared portfolio
        portfolio = SocialPortfolio(
            id=portfolio_id,
            account_id=account_id,
            user_id=current_user.id,
            display_name=share_settings.display_name,
            description=share_settings.description,
            is_public=share_settings.is_public,
            share_positions=share_settings.share_positions,
            share_performance=share_settings.share_performance,
            follower_count=0,
            total_return_percent=Decimal('0.00'),  # Would be calculated from actual account
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_social_portfolios[portfolio_id] = portfolio
        
        # Create activity
        activity_id = str(uuid.uuid4())
        activity = SocialActivity(
            id=activity_id,
            user_id=current_user.id,
            account_id=account_id,
            activity_type="share",
            content={
                "action": "shared_portfolio",
                "portfolio_name": share_settings.display_name,
                "is_public": share_settings.is_public
            },
            created_at=datetime.now()
        )
        mock_social_activities[activity_id] = activity
        
        return portfolio

@router.get("/portfolios", response_model=List[SocialPortfolio])
async def get_public_portfolios(
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("followers", regex="^(followers|performance|recent)$"),
    current_user = Depends(get_current_user)
):
    """Get public portfolios from the community"""
    public_portfolios = [
        portfolio for portfolio in mock_social_portfolios.values()
        if portfolio.is_public
    ]
    
    # Sort portfolios
    if sort_by == "followers":
        public_portfolios.sort(key=lambda x: x.follower_count, reverse=True)
    elif sort_by == "performance":
        public_portfolios.sort(key=lambda x: x.total_return_percent, reverse=True)
    elif sort_by == "recent":
        public_portfolios.sort(key=lambda x: x.updated_at, reverse=True)
    
    return public_portfolios[:limit]

@router.post("/portfolios/{portfolio_id}/follow")
async def follow_portfolio(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Follow a public portfolio"""
    if portfolio_id not in mock_social_portfolios:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = mock_social_portfolios[portfolio_id]
    if not portfolio.is_public:
        raise HTTPException(status_code=403, detail="Portfolio is private")
    
    # Check if already following
    follow_key = f"{current_user.id}_{portfolio_id}"
    if follow_key in mock_follows:
        raise HTTPException(status_code=400, detail="Already following this portfolio")
    
    # Create follow relationship
    mock_follows[follow_key] = {
        "follower_id": current_user.id,
        "portfolio_id": portfolio_id,
        "created_at": datetime.now()
    }
    
    # Update follower count
    portfolio.follower_count += 1
    portfolio.updated_at = datetime.now()
    
    # Create activity
    activity_id = str(uuid.uuid4())
    activity = SocialActivity(
        id=activity_id,
        user_id=current_user.id,
        account_id=portfolio.account_id,
        activity_type="follow",
        content={
            "action": "followed_portfolio",
            "portfolio_name": portfolio.display_name,
            "portfolio_owner": portfolio.user_id
        },
        created_at=datetime.now()
    )
    mock_social_activities[activity_id] = activity
    
    return {"message": "Portfolio followed successfully"}

@router.delete("/portfolios/{portfolio_id}/follow")
async def unfollow_portfolio(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Unfollow a portfolio"""
    if portfolio_id not in mock_social_portfolios:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = mock_social_portfolios[portfolio_id]
    
    # Check if following
    follow_key = f"{current_user.id}_{portfolio_id}"
    if follow_key not in mock_follows:
        raise HTTPException(status_code=400, detail="Not following this portfolio")
    
    # Remove follow relationship
    del mock_follows[follow_key]
    
    # Update follower count
    portfolio.follower_count = max(0, portfolio.follower_count - 1)
    portfolio.updated_at = datetime.now()
    
    return {"message": "Portfolio unfollowed successfully"}

@router.get("/feed", response_model=List[SocialFeedItem])
async def get_social_feed(
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get social feed with activities from followed portfolios"""
    # Get portfolios the user is following
    following_portfolios = [
        follow["portfolio_id"] for follow in mock_follows.values()
        if follow["follower_id"] == current_user.id
    ]
    
    # Get activities from followed portfolios
    feed_activities = []
    for activity in mock_social_activities.values():
        portfolio_id = None
        for pid, portfolio in mock_social_portfolios.items():
            if portfolio.account_id == activity.account_id:
                portfolio_id = pid
                break
        
        if portfolio_id in following_portfolios:
            # Get user display name
            portfolio = mock_social_portfolios[portfolio_id]
            feed_item = SocialFeedItem(
                id=activity.id,
                user_display_name=portfolio.display_name,
                activity_type=activity.activity_type,
                content=activity.content,
                created_at=activity.created_at
            )
            feed_activities.append(feed_item)
    
    # Sort by creation date (newest first)
    feed_activities.sort(key=lambda x: x.created_at, reverse=True)
    
    return feed_activities[:limit]

@router.get("/competitions", response_model=List[CompetitionInfo])
async def get_competitions(
    status: str = Query("active", regex="^(active|upcoming|ended)$"),
    current_user = Depends(get_current_user)
):
    """Get trading competitions"""
    now = datetime.now()
    competitions = []
    
    # Mock competitions data
    if not mock_competitions:
        # Create sample competitions
        comp1 = CompetitionInfo(
            id=str(uuid.uuid4()),
            name="Monthly Trading Challenge",
            description="Monthly paper trading competition with prizes",
            start_date=now.replace(day=1),
            end_date=now.replace(day=28),
            entry_fee=Decimal('0.00'),
            prize_pool=Decimal('5000.00'),
            participant_count=156,
            is_active=True,
            rules={
                "starting_balance": 100000,
                "max_position_size": 0.20,
                "allowed_assets": ["ATW", "IAM", "BCP", "OCP", "BMCE"]
            }
        )
        
        comp2 = CompetitionInfo(
            id=str(uuid.uuid4()),
            name="Ramadan Trading Cup",
            description="Special Ramadan trading competition",
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=60),
            entry_fee=Decimal('50.00'),
            prize_pool=Decimal('10000.00'),
            participant_count=0,
            is_active=False,
            rules={
                "starting_balance": 100000,
                "max_position_size": 0.15,
                "allowed_assets": ["ATW", "IAM", "BCP", "OCP", "BMCE", "CMT", "LAFA"]
            }
        )
        
        mock_competitions[comp1.id] = comp1
        mock_competitions[comp2.id] = comp2
    
    # Filter competitions by status
    for comp in mock_competitions.values():
        if status == "active" and comp.is_active and comp.start_date <= now <= comp.end_date:
            competitions.append(comp)
        elif status == "upcoming" and comp.start_date > now:
            competitions.append(comp)
        elif status == "ended" and comp.end_date < now:
            competitions.append(comp)
    
    return competitions

@router.post("/competitions/{competition_id}/join")
async def join_competition(
    competition_id: str,
    account_id: str,
    current_user = Depends(get_current_user)
):
    """Join a trading competition"""
    if competition_id not in mock_competitions:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    competition = mock_competitions[competition_id]
    
    # Check if competition is active and not started
    now = datetime.now()
    if competition.start_date <= now:
        raise HTTPException(status_code=400, detail="Competition has already started")
    
    # Create leaderboard entry
    leaderboard_key = f"{competition_id}_{current_user.id}"
    if leaderboard_key not in mock_leaderboards:
        leaderboard_entry = LeaderboardEntry(
            rank=0,
            user_id=current_user.id,
            display_name=f"User-{current_user.id[:8]}",
            account_id=account_id,
            total_return=Decimal('0.00'),
            total_return_percent=Decimal('0.00'),
            trades_count=0
        )
        mock_leaderboards[leaderboard_key] = leaderboard_entry
        
        # Update participant count
        competition.participant_count += 1
        
        return {"message": "Successfully joined competition"}
    else:
        raise HTTPException(status_code=400, detail="Already joined this competition")

@router.get("/competitions/{competition_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_competition_leaderboard(
    competition_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get competition leaderboard"""
    if competition_id not in mock_competitions:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    # Get leaderboard entries for this competition
    leaderboard_entries = [
        entry for key, entry in mock_leaderboards.items()
        if key.startswith(f"{competition_id}_")
    ]
    
    # Sort by total return percentage (descending)
    leaderboard_entries.sort(key=lambda x: x.total_return_percent, reverse=True)
    
    # Update ranks
    for i, entry in enumerate(leaderboard_entries):
        entry.rank = i + 1
    
    return leaderboard_entries[:limit]

@router.get("/my-following", response_model=List[SocialPortfolio])
async def get_my_following(
    current_user = Depends(get_current_user)
):
    """Get portfolios that the current user is following"""
    following_portfolio_ids = [
        follow["portfolio_id"] for follow in mock_follows.values()
        if follow["follower_id"] == current_user.id
    ]
    
    following_portfolios = [
        mock_social_portfolios[pid] for pid in following_portfolio_ids
        if pid in mock_social_portfolios
    ]
    
    return following_portfolios

@router.get("/my-followers", response_model=List[Dict[str, Any]])
async def get_my_followers(
    current_user = Depends(get_current_user)
):
    """Get users following current user's portfolios"""
    # Get current user's portfolios
    user_portfolios = [
        portfolio for portfolio in mock_social_portfolios.values()
        if portfolio.user_id == current_user.id
    ]
    
    followers = []
    for portfolio in user_portfolios:
        portfolio_followers = [
            follow for follow in mock_follows.values()
            if follow["portfolio_id"] == portfolio.id
        ]
        
        for follow in portfolio_followers:
            followers.append({
                "follower_id": follow["follower_id"],
                "portfolio_name": portfolio.display_name,
                "followed_at": follow["created_at"]
            })
    
    return followers

@router.get("/stats", response_model=Dict[str, Any])
async def get_social_stats(
    current_user = Depends(get_current_user)
):
    """Get social trading statistics"""
    # Get user's portfolios
    user_portfolios = [
        portfolio for portfolio in mock_social_portfolios.values()
        if portfolio.user_id == current_user.id
    ]
    
    total_followers = sum(portfolio.follower_count for portfolio in user_portfolios)
    
    # Get following count
    following_count = len([
        follow for follow in mock_follows.values()
        if follow["follower_id"] == current_user.id
    ])
    
    # Get competition participation
    competitions_joined = len([
        entry for key, entry in mock_leaderboards.items()
        if entry.user_id == current_user.id
    ])
    
    return {
        "shared_portfolios": len(user_portfolios),
        "total_followers": total_followers,
        "following_count": following_count,
        "competitions_joined": competitions_joined,
        "activities_count": len([
            activity for activity in mock_social_activities.values()
            if activity.user_id == current_user.id
        ])
    }