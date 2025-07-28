from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import asyncio
from sqlalchemy.orm import Session

from models.contest import (
    Contest, ContestEntry, ContestRanking, ContestResult, 
    ContestNotification, ContestStats, ContestStatus, ContestEntryStatus
)
from models.paper_trading import PaperTradingAccount, PaperTradingPosition
from utils.auth import get_current_user
from utils.cache import redis_client
from services.contest_service import ContestService

router = APIRouter(prefix="/contest", tags=["Contest"])

# Initialize contest service
contest_service = ContestService()

@router.get("/active", response_model=Contest)
async def get_active_contest():
    """Get the currently active contest"""
    try:
        contest = await contest_service.get_active_contest()
        if not contest:
            raise HTTPException(status_code=404, detail="No active contest found")
        return contest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active contest: {str(e)}")

@router.get("/rankings", response_model=List[ContestRanking])
async def get_contest_rankings(
    contest_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get contest rankings (top 10 by default)"""
    try:
        if not contest_id:
            # Get active contest
            active_contest = await contest_service.get_active_contest()
            if not active_contest:
                raise HTTPException(status_code=404, detail="No active contest found")
            contest_id = str(active_contest.id)
        
        rankings = await contest_service.get_contest_rankings(contest_id, limit)
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")

@router.post("/join", response_model=ContestEntry)
async def join_contest(
    account_id: str,
    current_user = Depends(get_current_user)
):
    """Join the active contest with a paper trading account"""
    try:
        # Validate account belongs to user
        account = await contest_service.validate_user_account(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found or access denied")
        
        # Check if user already joined
        existing_entry = await contest_service.get_user_contest_entry(current_user.id)
        if existing_entry:
            raise HTTPException(status_code=400, detail="Already joined the contest")
        
        # Check minimum positions requirement
        position_count = await contest_service.get_account_position_count(account_id)
        if position_count < 3:
            raise HTTPException(
                status_code=400, 
                detail=f"Minimum 3 positions required. Current: {position_count}"
            )
        
        # Join contest
        entry = await contest_service.join_contest(current_user.id, account_id)
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining contest: {str(e)}")

@router.post("/leave")
async def leave_contest(current_user = Depends(get_current_user)):
    """Leave the active contest"""
    try:
        success = await contest_service.leave_contest(current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="No active contest entry found")
        
        return {"message": "Successfully left the contest"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leaving contest: {str(e)}")

@router.get("/my-entry", response_model=ContestEntry)
async def get_my_contest_entry(current_user = Depends(get_current_user)):
    """Get current user's contest entry"""
    try:
        entry = await contest_service.get_user_contest_entry(current_user.id)
        if not entry:
            raise HTTPException(status_code=404, detail="No contest entry found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contest entry: {str(e)}")

@router.get("/notifications", response_model=List[ContestNotification])
async def get_contest_notifications(
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get contest notifications for current user"""
    try:
        notifications = await contest_service.get_user_notifications(current_user.id, limit)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        success = await contest_service.mark_notification_read(notification_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification read: {str(e)}")

@router.get("/stats", response_model=ContestStats)
async def get_contest_stats():
    """Get overall contest statistics"""
    try:
        stats = await contest_service.get_contest_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contest stats: {str(e)}")

# Admin endpoints
@router.post("/admin/create", response_model=Contest)
async def create_contest(
    contest_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Create a new contest (admin only)"""
    try:
        # Check if user is admin
        if not await contest_service.is_admin(current_user.id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        contest = await contest_service.create_contest(contest_data)
        return contest
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating contest: {str(e)}")

@router.post("/admin/{contest_id}/end", response_model=ContestResult)
async def end_contest(
    contest_id: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """End a contest and calculate results (admin only)"""
    try:
        # Check if user is admin
        if not await contest_service.is_admin(current_user.id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await contest_service.end_contest(contest_id)
        
        # Schedule prize distribution
        background_tasks.add_task(contest_service.distribute_prize, contest_id)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending contest: {str(e)}")

@router.post("/admin/{contest_id}/distribute-prize")
async def distribute_prize(
    contest_id: str,
    current_user = Depends(get_current_user)
):
    """Manually trigger prize distribution (admin only)"""
    try:
        # Check if user is admin
        if not await contest_service.is_admin(current_user.id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success = await contest_service.distribute_prize(contest_id)
        if not success:
            raise HTTPException(status_code=400, detail="Prize already distributed or contest not ended")
        
        return {"message": "Prize distributed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error distributing prize: {str(e)}")

# Background task to update rankings
@router.post("/admin/update-rankings")
async def update_rankings(background_tasks: BackgroundTasks):
    """Update all contest rankings (admin only)"""
    try:
        background_tasks.add_task(contest_service.update_all_rankings)
        return {"message": "Ranking update scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling ranking update: {str(e)}") 