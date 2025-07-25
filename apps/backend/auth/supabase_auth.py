#!/usr/bin/env python3
"""
Supabase Authentication Integration
Handles user authentication, watchlists, and alerts
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import requests
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@dataclass
class UserProfile:
    """User profile information"""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None

@dataclass
class WatchlistItem:
    """Watchlist item"""
    id: int
    user_id: str
    ticker: str
    company_name: str
    added_at: datetime
    notes: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: bool = True

@dataclass
class Alert:
    """Price alert"""
    id: int
    user_id: str
    ticker: str
    alert_type: str  # "price_above", "price_below", "percent_change"
    target_value: float
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None
    message: Optional[str] = None

class SupabaseAuth:
    """Supabase authentication handler"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.supabase_url, self.supabase_anon_key, self.supabase_service_key]):
            raise ValueError("Missing Supabase configuration")
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with Supabase"""
        try:
            # Decode token without verification first to get user ID
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Verify with Supabase
            headers = {
                "apikey": self.supabase_service_key,
                "Authorization": f"Bearer {self.supabase_service_key}"
            }
            
            response = requests.get(
                f"{self.supabase_url}/auth/v1/user",
                headers=headers,
                params={"access_token": token}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            user_data = response.json()
            return user_data
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
        """Get current authenticated user"""
        token = credentials.credentials
        user_data = await self.verify_token(token)
        
        return UserProfile(
            id=user_data.get("id"),
            email=user_data.get("email"),
            full_name=user_data.get("user_metadata", {}).get("full_name"),
            avatar_url=user_data.get("user_metadata", {}).get("avatar_url"),
            created_at=datetime.fromisoformat(user_data.get("created_at").replace("Z", "+00:00")) if user_data.get("created_at") else None,
            updated_at=datetime.fromisoformat(user_data.get("updated_at").replace("Z", "+00:00")) if user_data.get("updated_at") else None
        )

class WatchlistManager:
    """Manages user watchlists"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_user_watchlist(self, user_id: str) -> List[WatchlistItem]:
        """Get user's watchlist"""
        try:
            result = await self.db.execute(
                text("""
                    SELECT 
                        w.id,
                        w.user_id,
                        w.ticker,
                        c.name as company_name,
                        w.added_at,
                        w.notes,
                        w.target_price,
                        w.alert_enabled
                    FROM user_watchlists w
                    JOIN companies c ON w.ticker = c.ticker
                    WHERE w.user_id = :user_id
                    ORDER BY w.added_at DESC
                """),
                {"user_id": user_id}
            )
            
            watchlist = []
            for row in result.fetchall():
                watchlist.append(WatchlistItem(
                    id=row.id,
                    user_id=row.user_id,
                    ticker=row.ticker,
                    company_name=row.company_name,
                    added_at=row.added_at,
                    notes=row.notes,
                    target_price=float(row.target_price) if row.target_price else None,
                    alert_enabled=row.alert_enabled
                ))
            
            return watchlist
            
        except Exception as e:
            logger.error(f"Error getting watchlist for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get watchlist"
            )
    
    async def add_to_watchlist(self, user_id: str, ticker: str, notes: Optional[str] = None, target_price: Optional[float] = None) -> WatchlistItem:
        """Add company to user's watchlist"""
        try:
            # Check if already in watchlist
            existing = await self.db.execute(
                text("SELECT id FROM user_watchlists WHERE user_id = :user_id AND ticker = :ticker"),
                {"user_id": user_id, "ticker": ticker}
            )
            
            if existing.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company already in watchlist"
                )
            
            # Check if company exists
            company = await self.db.execute(
                text("SELECT name FROM companies WHERE ticker = :ticker"),
                {"ticker": ticker}
            )
            
            if not company.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            
            # Add to watchlist
            result = await self.db.execute(
                text("""
                    INSERT INTO user_watchlists (user_id, ticker, notes, target_price, alert_enabled, added_at)
                    VALUES (:user_id, :ticker, :notes, :target_price, TRUE, NOW())
                    RETURNING id, added_at
                """),
                {
                    "user_id": user_id,
                    "ticker": ticker,
                    "notes": notes,
                    "target_price": target_price
                }
            )
            
            row = result.fetchone()
            await self.db.commit()
            
            # Get company name
            company_result = await self.db.execute(
                text("SELECT name FROM companies WHERE ticker = :ticker"),
                {"ticker": ticker}
            )
            company_name = company_result.fetchone().name
            
            return WatchlistItem(
                id=row.id,
                user_id=user_id,
                ticker=ticker,
                company_name=company_name,
                added_at=row.added_at,
                notes=notes,
                target_price=target_price,
                alert_enabled=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add to watchlist"
            )
    
    async def remove_from_watchlist(self, user_id: str, ticker: str) -> bool:
        """Remove company from user's watchlist"""
        try:
            result = await self.db.execute(
                text("DELETE FROM user_watchlists WHERE user_id = :user_id AND ticker = :ticker"),
                {"user_id": user_id, "ticker": ticker}
            )
            
            await self.db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not in watchlist"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove from watchlist"
            )
    
    async def update_watchlist_item(self, user_id: str, ticker: str, notes: Optional[str] = None, target_price: Optional[float] = None, alert_enabled: Optional[bool] = None) -> WatchlistItem:
        """Update watchlist item"""
        try:
            # Build update query
            update_fields = []
            params = {"user_id": user_id, "ticker": ticker}
            
            if notes is not None:
                update_fields.append("notes = :notes")
                params["notes"] = notes
            
            if target_price is not None:
                update_fields.append("target_price = :target_price")
                params["target_price"] = target_price
            
            if alert_enabled is not None:
                update_fields.append("alert_enabled = :alert_enabled")
                params["alert_enabled"] = alert_enabled
            
            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            query = f"""
                UPDATE user_watchlists 
                SET {', '.join(update_fields)}
                WHERE user_id = :user_id AND ticker = :ticker
                RETURNING id, notes, target_price, alert_enabled, added_at
            """
            
            result = await self.db.execute(text(query), params)
            row = result.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not in watchlist"
                )
            
            await self.db.commit()
            
            # Get company name
            company_result = await self.db.execute(
                text("SELECT name FROM companies WHERE ticker = :ticker"),
                {"ticker": ticker}
            )
            company_name = company_result.fetchone().name
            
            return WatchlistItem(
                id=row.id,
                user_id=user_id,
                ticker=ticker,
                company_name=company_name,
                added_at=row.added_at,
                notes=row.notes,
                target_price=float(row.target_price) if row.target_price else None,
                alert_enabled=row.alert_enabled
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating watchlist item: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update watchlist item"
            )

class AlertManager:
    """Manages user price alerts"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_user_alerts(self, user_id: str) -> List[Alert]:
        """Get user's active alerts"""
        try:
            result = await self.db.execute(
                text("""
                    SELECT 
                        id,
                        user_id,
                        ticker,
                        alert_type,
                        target_value,
                        is_active,
                        created_at,
                        triggered_at,
                        message
                    FROM user_alerts
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {"user_id": user_id}
            )
            
            alerts = []
            for row in result.fetchall():
                alerts.append(Alert(
                    id=row.id,
                    user_id=row.user_id,
                    ticker=row.ticker,
                    alert_type=row.alert_type,
                    target_value=float(row.target_value),
                    is_active=row.is_active,
                    created_at=row.created_at,
                    triggered_at=row.triggered_at,
                    message=row.message
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get alerts"
            )
    
    async def create_alert(self, user_id: str, ticker: str, alert_type: str, target_value: float, message: Optional[str] = None) -> Alert:
        """Create a new price alert"""
        try:
            # Validate alert type
            valid_types = ["price_above", "price_below", "percent_change"]
            if alert_type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid alert type. Must be one of: {valid_types}"
                )
            
            # Check if company exists
            company = await self.db.execute(
                text("SELECT name FROM companies WHERE ticker = :ticker"),
                {"ticker": ticker}
            )
            
            if not company.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            
            # Create alert
            result = await self.db.execute(
                text("""
                    INSERT INTO user_alerts (user_id, ticker, alert_type, target_value, message, is_active, created_at)
                    VALUES (:user_id, :ticker, :alert_type, :target_value, :message, TRUE, NOW())
                    RETURNING id, created_at
                """),
                {
                    "user_id": user_id,
                    "ticker": ticker,
                    "alert_type": alert_type,
                    "target_value": target_value,
                    "message": message
                }
            )
            
            row = result.fetchone()
            await self.db.commit()
            
            return Alert(
                id=row.id,
                user_id=user_id,
                ticker=ticker,
                alert_type=alert_type,
                target_value=target_value,
                is_active=True,
                created_at=row.created_at,
                triggered_at=None,
                message=message
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create alert"
            )
    
    async def delete_alert(self, user_id: str, alert_id: int) -> bool:
        """Delete a price alert"""
        try:
            result = await self.db.execute(
                text("DELETE FROM user_alerts WHERE user_id = :user_id AND id = :alert_id"),
                {"user_id": user_id, "alert_id": alert_id}
            )
            
            await self.db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete alert"
            )
    
    async def toggle_alert(self, user_id: str, alert_id: int) -> Alert:
        """Toggle alert active status"""
        try:
            result = await self.db.execute(
                text("""
                    UPDATE user_alerts 
                    SET is_active = NOT is_active
                    WHERE user_id = :user_id AND id = :alert_id
                    RETURNING id, ticker, alert_type, target_value, is_active, created_at, triggered_at, message
                """),
                {"user_id": user_id, "alert_id": alert_id}
            )
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            await self.db.commit()
            
            return Alert(
                id=row.id,
                user_id=user_id,
                ticker=row.ticker,
                alert_type=row.alert_type,
                target_value=float(row.target_value),
                is_active=row.is_active,
                created_at=row.created_at,
                triggered_at=row.triggered_at,
                message=row.message
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error toggling alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle alert"
            )
    
    async def check_alerts(self, ticker: str, current_price: float, previous_price: float):
        """Check and trigger alerts for a ticker"""
        try:
            # Get all active alerts for this ticker
            result = await self.db.execute(
                text("""
                    SELECT id, user_id, alert_type, target_value, message
                    FROM user_alerts
                    WHERE ticker = :ticker AND is_active = TRUE
                """),
                {"ticker": ticker}
            )
            
            alerts = result.fetchall()
            triggered_alerts = []
            
            for alert in alerts:
                should_trigger = False
                alert_message = alert.message or f"Alert for {ticker}"
                
                if alert.alert_type == "price_above" and current_price >= alert.target_value:
                    should_trigger = True
                    alert_message = f"{ticker} price ({current_price}) is above target ({alert.target_value})"
                
                elif alert.alert_type == "price_below" and current_price <= alert.target_value:
                    should_trigger = True
                    alert_message = f"{ticker} price ({current_price}) is below target ({alert.target_value})"
                
                elif alert.alert_type == "percent_change":
                    percent_change = ((current_price - previous_price) / previous_price) * 100
                    if abs(percent_change) >= alert.target_value:
                        should_trigger = True
                        alert_message = f"{ticker} has changed by {percent_change:.2f}% (target: {alert.target_value}%)"
                
                if should_trigger:
                    # Mark alert as triggered
                    await self.db.execute(
                        text("""
                            UPDATE user_alerts 
                            SET triggered_at = NOW(), is_active = FALSE
                            WHERE id = :alert_id
                        """),
                        {"alert_id": alert.id}
                    )
                    
                    triggered_alerts.append({
                        "alert_id": alert.id,
                        "user_id": alert.user_id,
                        "ticker": ticker,
                        "message": alert_message,
                        "triggered_at": datetime.now()
                    })
            
            await self.db.commit()
            
            # Here you would send notifications to users
            # For now, just log the triggered alerts
            for alert in triggered_alerts:
                logger.info(f"Alert triggered: {alert}")
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts for {ticker}: {e}")

# Pydantic models for API requests/responses
class WatchlistAddRequest(BaseModel):
    ticker: str
    notes: Optional[str] = None
    target_price: Optional[float] = None

class WatchlistUpdateRequest(BaseModel):
    notes: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: Optional[bool] = None

class AlertCreateRequest(BaseModel):
    ticker: str
    alert_type: str
    target_value: float
    message: Optional[str] = None

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Dependency to get current authenticated user"""
    auth = SupabaseAuth()
    return await auth.get_current_user(credentials)

async def get_watchlist_manager(db: AsyncSession = Depends(get_db_session)) -> WatchlistManager:
    """Dependency to get watchlist manager"""
    return WatchlistManager(db)

async def get_alert_manager(db: AsyncSession = Depends(get_db_session)) -> AlertManager:
    """Dependency to get alert manager"""
    return AlertManager(db) 