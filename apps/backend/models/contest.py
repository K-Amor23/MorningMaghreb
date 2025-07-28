from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum

class ContestStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContestEntryStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    DISQUALIFIED = "disqualified"
    WITHDRAWN = "withdrawn"

class Contest(BaseModel):
    id: UUID
    name: str = "Monthly Portfolio Contest"
    description: str = "Monthly contest for best performing portfolio"
    start_date: date
    end_date: date
    status: ContestStatus = ContestStatus.ACTIVE
    prize_amount: Decimal = Field(default=100.00, description="Prize amount in USD")
    min_positions: int = Field(default=3, description="Minimum positions required")
    max_participants: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class ContestEntry(BaseModel):
    id: UUID
    contest_id: UUID
    user_id: UUID
    account_id: UUID  # Paper trading account ID
    username: str  # Anonymized or consented username
    initial_balance: Decimal
    current_balance: Decimal
    total_return: Decimal
    total_return_percent: Decimal
    position_count: int
    status: ContestEntryStatus = ContestEntryStatus.ACTIVE
    rank: Optional[int] = None
    joined_at: datetime
    updated_at: datetime

class ContestRanking(BaseModel):
    contest_id: UUID
    user_id: UUID
    username: str
    rank: int
    total_return_percent: Decimal
    total_return: Decimal
    position_count: int
    last_updated: datetime

class ContestResult(BaseModel):
    contest_id: UUID
    winner_id: Optional[UUID] = None
    winner_username: Optional[str] = None
    winner_return_percent: Optional[Decimal] = None
    total_participants: int
    average_return_percent: Decimal
    prize_distributed: bool = False
    distributed_at: Optional[datetime] = None
    created_at: datetime

class ContestNotification(BaseModel):
    id: UUID
    contest_id: UUID
    user_id: UUID
    notification_type: str  # "rank_change", "winner_announcement", "contest_start", "contest_end"
    message: str
    is_read: bool = False
    created_at: datetime

class ContestStats(BaseModel):
    total_contests: int
    active_contests: int
    total_participants: int
    total_prizes_awarded: Decimal
    average_participants_per_contest: float
    most_active_user: Optional[str] = None
    highest_single_return: Optional[Decimal] = None 