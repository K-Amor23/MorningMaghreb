import os
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from supabase import create_client, Client

from models.watchlist import (
    WatchlistCreate, WatchlistUpdate, WatchlistItemCreate, WatchlistItemUpdate,
    Watchlist, WatchlistWithItems, WatchlistSummary, WatchlistItem
)
from models.user import UserProfile

logger = logging.getLogger(__name__)

class WatchlistService:
    """Watchlist service using Supabase"""
    
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
    
    async def create_watchlist(self, user_id: str, watchlist_data: WatchlistCreate) -> Watchlist:
        """Create a new watchlist for a user"""
        try:
            if self.mock_mode:
                # Mock implementation for development
                watchlist_id = f"mock_watchlist_{datetime.utcnow().timestamp()}"
                return Watchlist(
                    id=watchlist_id,
                    user_id=user_id,
                    name=watchlist_data.name,
                    description=watchlist_data.description,
                    is_default=watchlist_data.is_default,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    item_count=0
                )
            
            # If this is the first watchlist or is_default is True, make it default
            existing_watchlists = self.supabase.table("watchlists").select("*").eq("user_id", user_id).execute()
            
            if not existing_watchlists.data or watchlist_data.is_default:
                # Set all other watchlists to not default
                if existing_watchlists.data:
                    self.supabase.table("watchlists").update({"is_default": False}).eq("user_id", user_id).execute()
            
            watchlist_data_dict = watchlist_data.dict()
            watchlist_data_dict["user_id"] = user_id
            watchlist_data_dict["created_at"] = datetime.utcnow().isoformat()
            watchlist_data_dict["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("watchlists").insert(watchlist_data_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create watchlist"
                )
            
            watchlist_data = response.data[0]
            
            return Watchlist(
                id=watchlist_data["id"],
                user_id=watchlist_data["user_id"],
                name=watchlist_data["name"],
                description=watchlist_data.get("description"),
                is_default=watchlist_data.get("is_default", False),
                created_at=datetime.fromisoformat(watchlist_data["created_at"]),
                updated_at=datetime.fromisoformat(watchlist_data["updated_at"]),
                item_count=0
            )
            
        except Exception as e:
            logger.error(f"Error creating watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create watchlist"
            )
    
    async def get_user_watchlists(self, user_id: str) -> List[WatchlistSummary]:
        """Get all watchlists for a user"""
        try:
            response = self.supabase.table("watchlists").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            watchlists = []
            for watchlist_data in response.data:
                # Get item count for each watchlist
                items_response = self.supabase.table("watchlist_items").select("id").eq("watchlist_id", watchlist_data["id"]).execute()
                item_count = len(items_response.data)
                
                watchlists.append(WatchlistSummary(
                    id=watchlist_data["id"],
                    name=watchlist_data["name"],
                    description=watchlist_data.get("description"),
                    is_default=watchlist_data.get("is_default", False),
                    item_count=item_count,
                    created_at=datetime.fromisoformat(watchlist_data["created_at"])
                ))
            
            return watchlists
            
        except Exception as e:
            logger.error(f"Error getting user watchlists: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get watchlists"
            )
    
    async def get_watchlist(self, watchlist_id: str, user_id: str) -> WatchlistWithItems:
        """Get a specific watchlist with its items"""
        try:
            # Get watchlist
            watchlist_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not watchlist_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            watchlist_data = watchlist_response.data[0]
            
            # Get watchlist items
            items_response = self.supabase.table("watchlist_items").select("*").eq("watchlist_id", watchlist_id).order("added_at", desc=True).execute()
            
            items = []
            for item_data in items_response.data:
                items.append(WatchlistItem(
                    id=item_data["id"],
                    ticker=item_data["ticker"],
                    added_at=datetime.fromisoformat(item_data["added_at"]),
                    notes=item_data.get("notes")
                ))
            
            return WatchlistWithItems(
                id=watchlist_data["id"],
                user_id=watchlist_data["user_id"],
                name=watchlist_data["name"],
                description=watchlist_data.get("description"),
                is_default=watchlist_data.get("is_default", False),
                created_at=datetime.fromisoformat(watchlist_data["created_at"]),
                updated_at=datetime.fromisoformat(watchlist_data["updated_at"]),
                item_count=len(items),
                items=items
            )
            
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get watchlist"
            )
    
    async def update_watchlist(self, watchlist_id: str, user_id: str, update_data: WatchlistUpdate) -> Watchlist:
        """Update a watchlist"""
        try:
            # Check if watchlist exists and belongs to user
            existing_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not existing_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            update_dict = {}
            if update_data.name is not None:
                update_dict["name"] = update_data.name
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.is_default is not None:
                update_dict["is_default"] = update_data.is_default
                
                # If setting as default, unset other watchlists
                if update_data.is_default:
                    self.supabase.table("watchlists").update({"is_default": False}).eq("user_id", user_id).neq("id", watchlist_id).execute()
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("watchlists").update(update_dict).eq("id", watchlist_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update watchlist"
                )
            
            watchlist_data = response.data[0]
            
            # Get item count
            items_response = self.supabase.table("watchlist_items").select("id").eq("watchlist_id", watchlist_id).execute()
            item_count = len(items_response.data)
            
            return Watchlist(
                id=watchlist_data["id"],
                user_id=watchlist_data["user_id"],
                name=watchlist_data["name"],
                description=watchlist_data.get("description"),
                is_default=watchlist_data.get("is_default", False),
                created_at=datetime.fromisoformat(watchlist_data["created_at"]),
                updated_at=datetime.fromisoformat(watchlist_data["updated_at"]),
                item_count=item_count
            )
            
        except Exception as e:
            logger.error(f"Error updating watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update watchlist"
            )
    
    async def delete_watchlist(self, watchlist_id: str, user_id: str) -> bool:
        """Delete a watchlist and all its items"""
        try:
            # Check if watchlist exists and belongs to user
            existing_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not existing_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            # Delete watchlist items first
            self.supabase.table("watchlist_items").delete().eq("watchlist_id", watchlist_id).execute()
            
            # Delete watchlist
            self.supabase.table("watchlists").delete().eq("id", watchlist_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete watchlist"
            )
    
    async def add_watchlist_item(self, watchlist_id: str, user_id: str, item_data: WatchlistItemCreate) -> WatchlistItem:
        """Add an item to a watchlist"""
        try:
            # Check if watchlist exists and belongs to user
            watchlist_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not watchlist_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            # Check if item already exists in watchlist
            existing_item = self.supabase.table("watchlist_items").select("*").eq("watchlist_id", watchlist_id).eq("ticker", item_data.ticker).execute()
            
            if existing_item.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Item already exists in watchlist"
                )
            
            # Add item
            item_dict = item_data.dict()
            item_dict["watchlist_id"] = watchlist_id
            item_dict["added_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("watchlist_items").insert(item_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add item to watchlist"
                )
            
            item_data = response.data[0]
            
            return WatchlistItem(
                id=item_data["id"],
                ticker=item_data["ticker"],
                added_at=datetime.fromisoformat(item_data["added_at"]),
                notes=item_data.get("notes")
            )
            
        except Exception as e:
            logger.error(f"Error adding watchlist item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add item to watchlist"
            )
    
    async def remove_watchlist_item(self, watchlist_id: str, user_id: str, ticker: str) -> bool:
        """Remove an item from a watchlist"""
        try:
            # Check if watchlist exists and belongs to user
            watchlist_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not watchlist_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            # Delete item
            response = self.supabase.table("watchlist_items").delete().eq("watchlist_id", watchlist_id).eq("ticker", ticker.upper()).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found in watchlist"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing watchlist item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove item from watchlist"
            )
    
    async def update_watchlist_item(self, watchlist_id: str, user_id: str, ticker: str, update_data: WatchlistItemUpdate) -> WatchlistItem:
        """Update a watchlist item"""
        try:
            # Check if watchlist exists and belongs to user
            watchlist_response = self.supabase.table("watchlists").select("*").eq("id", watchlist_id).eq("user_id", user_id).execute()
            
            if not watchlist_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Watchlist not found"
                )
            
            # Update item
            update_dict = {}
            if update_data.notes is not None:
                update_dict["notes"] = update_data.notes
            
            response = self.supabase.table("watchlist_items").update(update_dict).eq("watchlist_id", watchlist_id).eq("ticker", ticker.upper()).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found in watchlist"
                )
            
            item_data = response.data[0]
            
            return WatchlistItem(
                id=item_data["id"],
                ticker=item_data["ticker"],
                added_at=datetime.fromisoformat(item_data["added_at"]),
                notes=item_data.get("notes")
            )
            
        except Exception as e:
            logger.error(f"Error updating watchlist item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update watchlist item"
            )

# Create global instance
watchlist_service = WatchlistService() 