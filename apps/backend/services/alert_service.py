import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from supabase import create_client, Client

from models.alert import (
    AlertCreate, AlertUpdate, Alert, AlertType, AlertStatus
)
from models.user import UserProfile

logger = logging.getLogger(__name__)

class AlertService:
    """Alert service using Supabase with background checking"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def create_alert(self, user_id: str, alert_data: AlertCreate) -> Alert:
        """Create a new price alert for a user"""
        try:
            # Check if alert already exists for this user and ticker
            existing_alert = self.supabase.table("price_alerts").select("*").eq("user_id", user_id).eq("ticker", alert_data.ticker).eq("alert_type", alert_data.alert_type.value).execute()
            
            if existing_alert.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alert already exists for this ticker and type"
                )
            
            alert_dict = alert_data.dict()
            alert_dict["user_id"] = user_id
            alert_dict["alert_type"] = alert_data.alert_type.value
            alert_dict["created_at"] = datetime.utcnow().isoformat()
            alert_dict["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("price_alerts").insert(alert_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create alert"
                )
            
            alert_data = response.data[0]
            
            return Alert(
                id=alert_data["id"],
                user_id=alert_data["user_id"],
                ticker=alert_data["ticker"],
                alert_type=AlertType(alert_data["alert_type"]),
                target_value=Decimal(str(alert_data["price_threshold"])),
                current_value=None,
                is_active=alert_data.get("is_active", True),
                notes=alert_data.get("notes"),
                triggered_at=None,
                notification_sent=False,
                created_at=datetime.fromisoformat(alert_data["created_at"]),
                updated_at=datetime.fromisoformat(alert_data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create alert"
            )
    
    async def get_user_alerts(self, user_id: str) -> List[Alert]:
        """Get all alerts for a user"""
        try:
            response = self.supabase.table("price_alerts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            alerts = []
            for alert_data in response.data:
                alerts.append(Alert(
                    id=alert_data["id"],
                    user_id=alert_data["user_id"],
                    ticker=alert_data["ticker"],
                    alert_type=AlertType(alert_data["alert_type"]),
                    target_value=Decimal(str(alert_data["price_threshold"])),
                    current_value=None,  # Will be populated during checking
                    is_active=alert_data.get("is_active", True),
                    notes=alert_data.get("notes"),
                    triggered_at=datetime.fromisoformat(alert_data["triggered_at"]) if alert_data.get("triggered_at") else None,
                    notification_sent=alert_data.get("notification_sent", False),
                    created_at=datetime.fromisoformat(alert_data["created_at"]),
                    updated_at=datetime.fromisoformat(alert_data["updated_at"])
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get alerts"
            )
    
    async def get_alert(self, alert_id: str, user_id: str) -> Alert:
        """Get a specific alert"""
        try:
            response = self.supabase.table("price_alerts").select("*").eq("id", alert_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            alert_data = response.data[0]
            
            return Alert(
                id=alert_data["id"],
                user_id=alert_data["user_id"],
                ticker=alert_data["ticker"],
                alert_type=AlertType(alert_data["alert_type"]),
                target_value=Decimal(str(alert_data["price_threshold"])),
                current_value=None,
                is_active=alert_data.get("is_active", True),
                notes=alert_data.get("notes"),
                triggered_at=datetime.fromisoformat(alert_data["triggered_at"]) if alert_data.get("triggered_at") else None,
                notification_sent=alert_data.get("notification_sent", False),
                created_at=datetime.fromisoformat(alert_data["created_at"]),
                updated_at=datetime.fromisoformat(alert_data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error getting alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get alert"
            )
    
    async def update_alert(self, alert_id: str, user_id: str, update_data: AlertUpdate) -> Alert:
        """Update an alert"""
        try:
            # Check if alert exists and belongs to user
            existing_response = self.supabase.table("price_alerts").select("*").eq("id", alert_id).eq("user_id", user_id).execute()
            
            if not existing_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            update_dict = {}
            if update_data.alert_type is not None:
                update_dict["alert_type"] = update_data.alert_type.value
            if update_data.target_value is not None:
                update_dict["price_threshold"] = float(update_data.target_value)
            if update_data.notes is not None:
                update_dict["notes"] = update_data.notes
            if update_data.is_active is not None:
                update_dict["is_active"] = update_data.is_active
            
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("price_alerts").update(update_dict).eq("id", alert_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update alert"
                )
            
            alert_data = response.data[0]
            
            return Alert(
                id=alert_data["id"],
                user_id=alert_data["user_id"],
                ticker=alert_data["ticker"],
                alert_type=AlertType(alert_data["alert_type"]),
                target_value=Decimal(str(alert_data["price_threshold"])),
                current_value=None,
                is_active=alert_data.get("is_active", True),
                notes=alert_data.get("notes"),
                triggered_at=datetime.fromisoformat(alert_data["triggered_at"]) if alert_data.get("triggered_at") else None,
                notification_sent=alert_data.get("notification_sent", False),
                created_at=datetime.fromisoformat(alert_data["created_at"]),
                updated_at=datetime.fromisoformat(alert_data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error updating alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update alert"
            )
    
    async def delete_alert(self, alert_id: str, user_id: str) -> bool:
        """Delete an alert"""
        try:
            # Check if alert exists and belongs to user
            existing_response = self.supabase.table("price_alerts").select("*").eq("id", alert_id).eq("user_id", user_id).execute()
            
            if not existing_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            # Delete alert
            self.supabase.table("price_alerts").delete().eq("id", alert_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete alert"
            )
    
    async def check_alerts(self) -> List[Alert]:
        """Background job to check all active alerts"""
        try:
            # Get all active alerts
            response = self.supabase.table("price_alerts").select("*").eq("is_active", True).execute()
            
            triggered_alerts = []
            
            for alert_data in response.data:
                try:
                    # Get current market data for the ticker
                    current_price = await self._get_current_price(alert_data["ticker"])
                    
                    if current_price is None:
                        continue
                    
                    # Check if alert should be triggered
                    should_trigger = await self._check_alert_condition(
                        alert_data["alert_type"],
                        current_price,
                        Decimal(str(alert_data["price_threshold"]))
                    )
                    
                    if should_trigger:
                        # Update alert as triggered
                        update_dict = {
                            "triggered_at": datetime.utcnow().isoformat(),
                            "notification_sent": True,
                            "updated_at": datetime.utcnow().isoformat()
                        }
                        
                        self.supabase.table("price_alerts").update(update_dict).eq("id", alert_data["id"]).execute()
                        
                        # Add to triggered alerts list
                        triggered_alerts.append(Alert(
                            id=alert_data["id"],
                            user_id=alert_data["user_id"],
                            ticker=alert_data["ticker"],
                            alert_type=AlertType(alert_data["alert_type"]),
                            target_value=Decimal(str(alert_data["price_threshold"])),
                            current_value=current_price,
                            is_active=False,  # Mark as inactive after triggering
                            notes=alert_data.get("notes"),
                            triggered_at=datetime.utcnow(),
                            notification_sent=True,
                            created_at=datetime.fromisoformat(alert_data["created_at"]),
                            updated_at=datetime.utcnow()
                        ))
                        
                        # Send notification (in a real implementation)
                        await self._send_notification(alert_data["user_id"], alert_data["ticker"], alert_data["alert_type"], current_price)
                        
                except Exception as e:
                    logger.error(f"Error checking alert {alert_data['id']}: {e}")
                    continue
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    async def _get_current_price(self, ticker: str) -> Optional[Decimal]:
        """Get current price for a ticker (mock implementation)"""
        try:
            # In a real implementation, this would fetch from market data API
            # For now, return a mock price
            mock_prices = {
                "IAM": Decimal("12.50"),
                "ATW": Decimal("45.20"),
                "BCP": Decimal("18.75"),
                "BMCE": Decimal("22.30"),
                "CIH": Decimal("15.80")
            }
            
            return mock_prices.get(ticker, Decimal("10.00"))
            
        except Exception as e:
            logger.error(f"Error getting current price for {ticker}: {e}")
            return None
    
    async def _check_alert_condition(self, alert_type: str, current_price: Decimal, target_value: Decimal) -> bool:
        """Check if an alert condition is met"""
        try:
            if alert_type == "above":
                return current_price >= target_value
            elif alert_type == "below":
                return current_price <= target_value
            elif alert_type == "change_percent":
                # This would require previous price data
                return False
            elif alert_type == "volume_spike":
                # This would require volume data
                return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking alert condition: {e}")
            return False
    
    async def _send_notification(self, user_id: str, ticker: str, alert_type: str, current_price: Decimal):
        """Send notification to user (mock implementation)"""
        try:
            # In a real implementation, this would send email, SMS, or push notification
            logger.info(f"Alert triggered for user {user_id}: {ticker} {alert_type} at {current_price}")
            
            # You could integrate with:
            # - Email service (SendGrid, AWS SES)
            # - SMS service (Twilio)
            # - Push notifications (Firebase)
            # - WebSocket for real-time notifications
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

# Create global instance
alert_service = AlertService() 