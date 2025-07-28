from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from models.watchlist import (
    WatchlistCreate, WatchlistUpdate, WatchlistItemCreate, WatchlistItemUpdate,
    WatchlistResponse, WatchlistListResponse, WatchlistCreateResponse,
    WatchlistUpdateResponse, WatchlistDeleteResponse, WatchlistItemResponse,
    WatchlistItemCreateResponse, WatchlistItemUpdateResponse, WatchlistItemDeleteResponse,
    WatchlistItemListResponse
)
from models.user import UserProfile
from services.watchlist_service import watchlist_service
from services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return await auth_service.get_current_user(token)

@router.get("/", response_model=WatchlistListResponse)
async def get_user_watchlists(current_user: UserProfile = Depends(get_current_user)):
    """Get all watchlists for the current user"""
    watchlists = await watchlist_service.get_user_watchlists(current_user.id)
    return WatchlistListResponse(
        watchlists=watchlists,
        total_count=len(watchlists)
    )

@router.post("/", response_model=WatchlistCreateResponse)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new watchlist for the current user"""
    watchlist = await watchlist_service.create_watchlist(current_user.id, watchlist_data)
    return WatchlistCreateResponse(watchlist=watchlist)

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get a specific watchlist with its items"""
    watchlist = await watchlist_service.get_watchlist(watchlist_id, current_user.id)
    return WatchlistResponse(watchlist=watchlist)

@router.put("/{watchlist_id}", response_model=WatchlistUpdateResponse)
async def update_watchlist(
    watchlist_id: str,
    update_data: WatchlistUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a watchlist"""
    watchlist = await watchlist_service.update_watchlist(watchlist_id, current_user.id, update_data)
    return WatchlistUpdateResponse(watchlist=watchlist)

@router.delete("/{watchlist_id}", response_model=WatchlistDeleteResponse)
async def delete_watchlist(
    watchlist_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a watchlist and all its items"""
    await watchlist_service.delete_watchlist(watchlist_id, current_user.id)
    return WatchlistDeleteResponse()

@router.post("/{watchlist_id}/items", response_model=WatchlistItemCreateResponse)
async def add_watchlist_item(
    watchlist_id: str,
    item_data: WatchlistItemCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Add an item to a watchlist"""
    item = await watchlist_service.add_watchlist_item(watchlist_id, current_user.id, item_data)
    return WatchlistItemCreateResponse(item=item)

@router.delete("/{watchlist_id}/items/{ticker}", response_model=WatchlistItemDeleteResponse)
async def remove_watchlist_item(
    watchlist_id: str,
    ticker: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Remove an item from a watchlist"""
    await watchlist_service.remove_watchlist_item(watchlist_id, current_user.id, ticker)
    return WatchlistItemDeleteResponse()

@router.put("/{watchlist_id}/items/{ticker}", response_model=WatchlistItemUpdateResponse)
async def update_watchlist_item(
    watchlist_id: str,
    ticker: str,
    update_data: WatchlistItemUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a watchlist item"""
    item = await watchlist_service.update_watchlist_item(watchlist_id, current_user.id, ticker, update_data)
    return WatchlistItemUpdateResponse(item=item)

@router.get("/{watchlist_id}/items", response_model=WatchlistItemListResponse)
async def get_watchlist_items(
    watchlist_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get all items in a watchlist"""
    watchlist = await watchlist_service.get_watchlist(watchlist_id, current_user.id)
    return WatchlistItemListResponse(
        items=watchlist.items,
        total_count=len(watchlist.items)
    ) 