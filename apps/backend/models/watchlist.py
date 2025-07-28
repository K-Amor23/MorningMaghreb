from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class WatchlistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_default: bool = False

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_default: Optional[bool] = None

class WatchlistItem(BaseModel):
    id: str
    ticker: str = Field(..., min_length=1, max_length=10)
    added_at: datetime
    notes: Optional[str] = Field(None, max_length=500)

class WatchlistItemCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('ticker')
    def validate_ticker(cls, v):
        # Ensure ticker is uppercase
        return v.upper()

class WatchlistItemUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=500)

class Watchlist(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime
    item_count: int = 0

class WatchlistWithItems(Watchlist):
    items: List[WatchlistItem] = []

class WatchlistSummary(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_default: bool
    item_count: int
    created_at: datetime

class WatchlistResponse(BaseModel):
    watchlist: WatchlistWithItems
    message: str = "Watchlist retrieved successfully"

class WatchlistListResponse(BaseModel):
    watchlists: List[WatchlistSummary]
    total_count: int
    message: str = "Watchlists retrieved successfully"

class WatchlistCreateResponse(BaseModel):
    watchlist: Watchlist
    message: str = "Watchlist created successfully"

class WatchlistUpdateResponse(BaseModel):
    watchlist: Watchlist
    message: str = "Watchlist updated successfully"

class WatchlistDeleteResponse(BaseModel):
    message: str = "Watchlist deleted successfully"

class WatchlistItemResponse(BaseModel):
    item: WatchlistItem
    message: str = "Watchlist item retrieved successfully"

class WatchlistItemCreateResponse(BaseModel):
    item: WatchlistItem
    message: str = "Watchlist item added successfully"

class WatchlistItemUpdateResponse(BaseModel):
    item: WatchlistItem
    message: str = "Watchlist item updated successfully"

class WatchlistItemDeleteResponse(BaseModel):
    message: str = "Watchlist item removed successfully"

class WatchlistItemListResponse(BaseModel):
    items: List[WatchlistItem]
    total_count: int
    message: str = "Watchlist items retrieved successfully" 