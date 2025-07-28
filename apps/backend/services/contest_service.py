import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models.contest import (
    Contest, ContestEntry, ContestRanking, ContestResult, 
    ContestNotification, ContestStats, ContestStatus, ContestEntryStatus
)
from models.paper_trading import PaperTradingAccount, PaperTradingPosition
from utils.cache import redis_client
from database.connection import get_db

logger = logging.getLogger(__name__)

class ContestService:
    """Service for managing portfolio contests"""
    
    def __init__(self):
        self.cache_key_prefix = "contest:"
    
    async def get_active_contest(self) -> Optional[Contest]:
        """Get the currently active contest"""
        try:
            # Check cache first
            cache_key = f"{self.cache_key_prefix}active"
            cached = await redis_client.get(cache_key)
            if cached:
                return Contest.parse_raw(cached)
            
            # Query database
            db = next(get_db())
            contest = db.query(Contest).filter(
                Contest.status == ContestStatus.ACTIVE,
                Contest.start_date <= date.today(),
                Contest.end_date >= date.today()
            ).first()
            
            if contest:
                # Cache for 5 minutes
                await redis_client.setex(
                    cache_key, 
                    300, 
                    contest.json()
                )
            
            return contest
        except Exception as e:
            logger.error(f"Error getting active contest: {e}")
            return None
    
    async def get_contest_rankings(self, contest_id: str, limit: int = 10) -> List[ContestRanking]:
        """Get contest rankings ordered by return percentage"""
        try:
            # Check cache first
            cache_key = f"{self.cache_key_prefix}rankings:{contest_id}:{limit}"
            cached = await redis_client.get(cache_key)
            if cached:
                return [ContestRanking.parse_raw(item) for item in cached]
            
            # Query database
            db = next(get_db())
            entries = db.query(ContestEntry).filter(
                ContestEntry.contest_id == contest_id,
                ContestEntry.status == ContestEntryStatus.ACTIVE
            ).order_by(desc(ContestEntry.total_return_percent)).limit(limit).all()
            
            rankings = []
            for i, entry in enumerate(entries, 1):
                ranking = ContestRanking(
                    contest_id=contest_id,
                    user_id=entry.user_id,
                    username=entry.username,
                    rank=i,
                    total_return_percent=entry.total_return_percent,
                    total_return=entry.total_return,
                    position_count=entry.position_count,
                    last_updated=entry.updated_at
                )
                rankings.append(ranking)
            
            # Cache for 1 minute
            if rankings:
                await redis_client.setex(
                    cache_key,
                    60,
                    [ranking.json() for ranking in rankings]
                )
            
            return rankings
        except Exception as e:
            logger.error(f"Error getting contest rankings: {e}")
            return []
    
    async def validate_user_account(self, account_id: str, user_id: str) -> Optional[PaperTradingAccount]:
        """Validate that account belongs to user"""
        try:
            db = next(get_db())
            account = db.query(PaperTradingAccount).filter(
                PaperTradingAccount.id == account_id,
                PaperTradingAccount.user_id == user_id,
                PaperTradingAccount.is_active == True
            ).first()
            return account
        except Exception as e:
            logger.error(f"Error validating user account: {e}")
            return None
    
    async def get_user_contest_entry(self, user_id: str) -> Optional[ContestEntry]:
        """Get user's current contest entry"""
        try:
            db = next(get_db())
            entry = db.query(ContestEntry).filter(
                ContestEntry.user_id == user_id,
                ContestEntry.status == ContestEntryStatus.ACTIVE
            ).first()
            return entry
        except Exception as e:
            logger.error(f"Error getting user contest entry: {e}")
            return None
    
    async def get_account_position_count(self, account_id: str) -> int:
        """Get number of positions in account"""
        try:
            db = next(get_db())
            count = db.query(PaperTradingPosition).filter(
                PaperTradingPosition.account_id == account_id,
                PaperTradingPosition.quantity > 0
            ).count()
            return count
        except Exception as e:
            logger.error(f"Error getting position count: {e}")
            return 0
    
    async def join_contest(self, user_id: str, account_id: str) -> ContestEntry:
        """Join the active contest"""
        try:
            db = next(get_db())
            
            # Get active contest
            contest = await self.get_active_contest()
            if not contest:
                raise ValueError("No active contest found")
            
            # Get account details
            account = await self.validate_user_account(account_id, user_id)
            if not account:
                raise ValueError("Invalid account")
            
            # Calculate current performance
            total_return = account.current_balance - account.initial_balance
            total_return_percent = (
                (total_return / account.initial_balance * 100)
                if account.initial_balance > 0 else Decimal('0.00')
            )
            
            position_count = await self.get_account_position_count(account_id)
            
            # Create contest entry
            entry = ContestEntry(
                id=str(uuid.uuid4()),
                contest_id=contest.id,
                user_id=user_id,
                account_id=account_id,
                username=f"Trader_{user_id[-8:]}",  # Anonymized username
                initial_balance=account.initial_balance,
                current_balance=account.current_balance,
                total_return=total_return,
                total_return_percent=total_return_percent,
                position_count=position_count,
                joined_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(entry)
            db.commit()
            
            # Clear cache
            await redis_client.delete(f"{self.cache_key_prefix}active")
            await redis_client.delete(f"{self.cache_key_prefix}rankings:{contest.id}:*")
            
            # Send notification
            await self._send_notification(
                user_id, 
                contest.id, 
                "contest_join", 
                "You have successfully joined the monthly portfolio contest!"
            )
            
            return entry
        except Exception as e:
            logger.error(f"Error joining contest: {e}")
            raise
    
    async def leave_contest(self, user_id: str) -> bool:
        """Leave the active contest"""
        try:
            db = next(get_db())
            
            entry = await self.get_user_contest_entry(user_id)
            if not entry:
                return False
            
            # Update entry status
            entry.status = ContestEntryStatus.WITHDRAWN
            entry.updated_at = datetime.now()
            
            db.commit()
            
            # Clear cache
            await redis_client.delete(f"{self.cache_key_prefix}active")
            await redis_client.delete(f"{self.cache_key_prefix}rankings:{entry.contest_id}:*")
            
            # Send notification
            await self._send_notification(
                user_id,
                entry.contest_id,
                "contest_leave",
                "You have left the monthly portfolio contest."
            )
            
            return True
        except Exception as e:
            logger.error(f"Error leaving contest: {e}")
            return False
    
    async def update_contest_rankings(self, contest_id: str):
        """Update rankings for a specific contest"""
        try:
            db = next(get_db())
            
            # Get all active entries for the contest
            entries = db.query(ContestEntry).filter(
                ContestEntry.contest_id == contest_id,
                ContestEntry.status == ContestEntryStatus.ACTIVE
            ).all()
            
            # Update performance for each entry
            for entry in entries:
                # Get current account performance
                account = db.query(PaperTradingAccount).filter(
                    PaperTradingAccount.id == entry.account_id
                ).first()
                
                if account:
                    total_return = account.current_balance - entry.initial_balance
                    total_return_percent = (
                        (total_return / entry.initial_balance * 100)
                        if entry.initial_balance > 0 else Decimal('0.00')
                    )
                    
                    position_count = await self.get_account_position_count(entry.account_id)
                    
                    # Update entry
                    entry.current_balance = account.current_balance
                    entry.total_return = total_return
                    entry.total_return_percent = total_return_percent
                    entry.position_count = position_count
                    entry.updated_at = datetime.now()
            
            db.commit()
            
            # Clear cache
            await redis_client.delete(f"{self.cache_key_prefix}rankings:{contest_id}:*")
            
            # Check for rank changes and send notifications
            await self._check_rank_changes(contest_id)
            
        except Exception as e:
            logger.error(f"Error updating contest rankings: {e}")
    
    async def _check_rank_changes(self, contest_id: str):
        """Check for rank changes and send notifications"""
        try:
            current_rankings = await self.get_contest_rankings(contest_id, 100)
            
            # Get previous rankings from cache
            cache_key = f"{self.cache_key_prefix}previous_rankings:{contest_id}"
            previous_data = await redis_client.get(cache_key)
            
            if previous_data:
                previous_rankings = [ContestRanking.parse_raw(item) for item in previous_data]
                
                # Compare rankings
                for current in current_rankings:
                    previous = next(
                        (p for p in previous_rankings if p.user_id == current.user_id), 
                        None
                    )
                    
                    if previous and current.rank < previous.rank:
                        # User moved up in rankings
                        await self._send_notification(
                            current.user_id,
                            contest_id,
                            "rank_change",
                            f"Congratulations! You moved up to #{current.rank} in the contest!"
                        )
                    elif previous and current.rank > previous.rank:
                        # User moved down in rankings
                        await self._send_notification(
                            current.user_id,
                            contest_id,
                            "rank_change",
                            f"You are now ranked #{current.rank} in the contest."
                        )
            
            # Store current rankings for next comparison
            await redis_client.setex(
                cache_key,
                3600,  # 1 hour
                [ranking.json() for ranking in current_rankings]
            )
            
        except Exception as e:
            logger.error(f"Error checking rank changes: {e}")
    
    async def _send_notification(self, user_id: str, contest_id: str, notification_type: str, message: str):
        """Send a contest notification"""
        try:
            db = next(get_db())
            
            notification = ContestNotification(
                id=str(uuid.uuid4()),
                contest_id=contest_id,
                user_id=user_id,
                notification_type=notification_type,
                message=message,
                created_at=datetime.now()
            )
            
            db.add(notification)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def get_user_notifications(self, user_id: str, limit: int = 20) -> List[ContestNotification]:
        """Get notifications for a user"""
        try:
            db = next(get_db())
            notifications = db.query(ContestNotification).filter(
                ContestNotification.user_id == user_id
            ).order_by(desc(ContestNotification.created_at)).limit(limit).all()
            
            return notifications
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        try:
            db = next(get_db())
            notification = db.query(ContestNotification).filter(
                ContestNotification.id == notification_id,
                ContestNotification.user_id == user_id
            ).first()
            
            if notification:
                notification.is_read = True
                db.commit()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error marking notification read: {e}")
            return False
    
    async def get_contest_stats(self) -> ContestStats:
        """Get overall contest statistics"""
        try:
            db = next(get_db())
            
            total_contests = db.query(Contest).count()
            active_contests = db.query(Contest).filter(
                Contest.status == ContestStatus.ACTIVE
            ).count()
            total_participants = db.query(ContestEntry).filter(
                ContestEntry.status == ContestEntryStatus.ACTIVE
            ).count()
            
            # Calculate total prizes awarded
            total_prizes = db.query(func.sum(Contest.prize_amount)).filter(
                Contest.status == ContestStatus.COMPLETED
            ).scalar() or Decimal('0.00')
            
            # Calculate average participants per contest
            avg_participants = (
                total_participants / total_contests if total_contests > 0 else 0
            )
            
            # Get most active user
            most_active = db.query(ContestEntry.user_id, func.count(ContestEntry.id)).group_by(
                ContestEntry.user_id
            ).order_by(desc(func.count(ContestEntry.id))).first()
            
            most_active_user = most_active[0] if most_active else None
            
            # Get highest single return
            highest_return = db.query(func.max(ContestEntry.total_return_percent)).scalar()
            
            return ContestStats(
                total_contests=total_contests,
                active_contests=active_contests,
                total_participants=total_participants,
                total_prizes_awarded=total_prizes,
                average_participants_per_contest=avg_participants,
                most_active_user=most_active_user,
                highest_single_return=highest_return
            )
        except Exception as e:
            logger.error(f"Error getting contest stats: {e}")
            return ContestStats(
                total_contests=0,
                active_contests=0,
                total_participants=0,
                total_prizes_awarded=Decimal('0.00'),
                average_participants_per_contest=0.0
            )
    
    async def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        try:
            db = next(get_db())
            # This would check against a user roles table
            # For now, return True for demo purposes
            return True
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
    
    async def create_contest(self, contest_data: Dict[str, Any]) -> Contest:
        """Create a new contest"""
        try:
            db = next(get_db())
            
            contest = Contest(
                id=str(uuid.uuid4()),
                name=contest_data.get("name", "Monthly Portfolio Contest"),
                description=contest_data.get("description", "Monthly contest for best performing portfolio"),
                start_date=contest_data["start_date"],
                end_date=contest_data["end_date"],
                prize_amount=Decimal(str(contest_data.get("prize_amount", 100.00))),
                min_positions=contest_data.get("min_positions", 3),
                max_participants=contest_data.get("max_participants"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(contest)
            db.commit()
            
            # Clear cache
            await redis_client.delete(f"{self.cache_key_prefix}active")
            
            return contest
        except Exception as e:
            logger.error(f"Error creating contest: {e}")
            raise
    
    async def end_contest(self, contest_id: str) -> ContestResult:
        """End a contest and calculate results"""
        try:
            db = next(get_db())
            
            # Get contest
            contest = db.query(Contest).filter(Contest.id == contest_id).first()
            if not contest:
                raise ValueError("Contest not found")
            
            # Update contest status
            contest.status = ContestStatus.COMPLETED
            contest.updated_at = datetime.now()
            
            # Get final rankings
            final_rankings = await self.get_contest_rankings(contest_id, 1)
            
            winner = final_rankings[0] if final_rankings else None
            
            # Calculate average return
            entries = db.query(ContestEntry).filter(
                ContestEntry.contest_id == contest_id,
                ContestEntry.status == ContestEntryStatus.ACTIVE
            ).all()
            
            total_participants = len(entries)
            average_return = (
                sum(entry.total_return_percent for entry in entries) / total_participants
                if total_participants > 0 else Decimal('0.00')
            )
            
            # Create result
            result = ContestResult(
                contest_id=contest_id,
                winner_id=winner.user_id if winner else None,
                winner_username=winner.username if winner else None,
                winner_return_percent=winner.total_return_percent if winner else None,
                total_participants=total_participants,
                average_return_percent=average_return,
                created_at=datetime.now()
            )
            
            db.add(result)
            db.commit()
            
            # Send winner notification
            if winner:
                await self._send_notification(
                    winner.user_id,
                    contest_id,
                    "winner_announcement",
                    f"Congratulations! You won the contest with a {winner.total_return_percent:.2f}% return!"
                )
            
            # Clear cache
            await redis_client.delete(f"{self.cache_key_prefix}active")
            await redis_client.delete(f"{self.cache_key_prefix}rankings:{contest_id}:*")
            
            return result
        except Exception as e:
            logger.error(f"Error ending contest: {e}")
            raise
    
    async def distribute_prize(self, contest_id: str) -> bool:
        """Distribute prize to contest winner"""
        try:
            db = next(get_db())
            
            # Get contest result
            result = db.query(ContestResult).filter(
                ContestResult.contest_id == contest_id
            ).first()
            
            if not result or result.prize_distributed:
                return False
            
            # Update result
            result.prize_distributed = True
            result.distributed_at = datetime.now()
            
            db.commit()
            
            # In a real implementation, this would integrate with a payment system
            # For now, just log the distribution
            logger.info(f"Prize distributed for contest {contest_id}: ${result.winner_return_percent}")
            
            return True
        except Exception as e:
            logger.error(f"Error distributing prize: {e}")
            return False
    
    async def update_all_rankings(self):
        """Update rankings for all active contests"""
        try:
            db = next(get_db())
            active_contests = db.query(Contest).filter(
                Contest.status == ContestStatus.ACTIVE
            ).all()
            
            for contest in active_contests:
                await self.update_contest_rankings(str(contest.id))
                
        except Exception as e:
            logger.error(f"Error updating all rankings: {e}") 