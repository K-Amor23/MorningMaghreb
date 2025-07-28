from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import the notification service
from services.notification_service import (
    notification_service, 
    NotificationPreferences, 
    NotificationPayload, 
    NotificationType, 
    NotificationChannel
)

# Configure logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models
class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: Dict[str, str]

class NotificationPreferencesRequest(BaseModel):
    web_push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    price_alerts: Optional[bool] = None
    portfolio_updates: Optional[bool] = None
    market_updates: Optional[bool] = None
    news_alerts: Optional[bool] = None
    system_alerts: Optional[bool] = None
    backtest_notifications: Optional[bool] = None
    risk_alerts: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class SendNotificationRequest(BaseModel):
    user_id: str
    notification_type: str
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    image: Optional[str] = None
    tag: Optional[str] = None
    data: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    require_interaction: Optional[bool] = False
    silent: Optional[bool] = False
    channels: Optional[List[str]] = None

class NotificationHistoryItem(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    type: str
    data: Optional[Dict] = None
    read: bool
    created_at: datetime

# Mock token verification (replace with actual implementation)
async def verify_token(token: str):
    """Verify JWT token and return user info"""
    # Mock implementation - replace with actual token verification
    class MockUser:
        def __init__(self):
            self.id = "mock_user_id"
            self.subscription_tier = "pro"
    
    return MockUser()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    try:
        user = await verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

router = APIRouter()

@router.post("/subscriptions")
async def add_push_subscription(
    request: PushSubscriptionRequest,
    current_user = Depends(get_current_user)
):
    """Add a new push notification subscription"""
    try:
        success = notification_service.add_push_subscription(
            user_id=current_user.id,
            subscription={
                'endpoint': request.endpoint,
                'keys': request.keys
            }
        )
        
        if success:
            return {
                "message": "Push subscription added successfully",
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add push subscription")
    except Exception as e:
        logger.error(f"Error adding push subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to add push subscription")

@router.delete("/subscriptions/{endpoint}")
async def remove_push_subscription(
    endpoint: str,
    current_user = Depends(get_current_user)
):
    """Remove a push notification subscription"""
    try:
        success = notification_service.remove_push_subscription(
            user_id=current_user.id,
            endpoint=endpoint
        )
        
        if success:
            return {
                "message": "Push subscription removed successfully",
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to remove push subscription")
    except Exception as e:
        logger.error(f"Error removing push subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove push subscription")

@router.get("/subscriptions")
async def get_push_subscriptions(current_user = Depends(get_current_user)):
    """Get user's push notification subscriptions"""
    try:
        subscriptions = notification_service.get_user_subscriptions(current_user.id)
        return {
            "user_id": current_user.id,
            "subscriptions": subscriptions
        }
    except Exception as e:
        logger.error(f"Error getting push subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get push subscriptions")

@router.get("/preferences")
async def get_notification_preferences(current_user = Depends(get_current_user)):
    """Get user's notification preferences"""
    try:
        preferences = notification_service.get_user_preferences(current_user.id)
        if preferences:
            return {
                "user_id": current_user.id,
                "preferences": {
                    "web_push_enabled": preferences.web_push_enabled,
                    "email_enabled": preferences.email_enabled,
                    "sms_enabled": preferences.sms_enabled,
                    "in_app_enabled": preferences.in_app_enabled,
                    "price_alerts": preferences.price_alerts,
                    "portfolio_updates": preferences.portfolio_updates,
                    "market_updates": preferences.market_updates,
                    "news_alerts": preferences.news_alerts,
                    "system_alerts": preferences.system_alerts,
                    "backtest_notifications": preferences.backtest_notifications,
                    "risk_alerts": preferences.risk_alerts,
                    "quiet_hours_start": preferences.quiet_hours_start,
                    "quiet_hours_end": preferences.quiet_hours_end,
                    "timezone": preferences.timezone
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Preferences not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification preferences")

@router.put("/preferences")
async def update_notification_preferences(
    request: NotificationPreferencesRequest,
    current_user = Depends(get_current_user)
):
    """Update user's notification preferences"""
    try:
        # Get current preferences
        current_preferences = notification_service.get_user_preferences(current_user.id)
        if not current_preferences:
            current_preferences = NotificationPreferences(user_id=current_user.id)
        
        # Update only provided fields
        if request.web_push_enabled is not None:
            current_preferences.web_push_enabled = request.web_push_enabled
        if request.email_enabled is not None:
            current_preferences.email_enabled = request.email_enabled
        if request.sms_enabled is not None:
            current_preferences.sms_enabled = request.sms_enabled
        if request.in_app_enabled is not None:
            current_preferences.in_app_enabled = request.in_app_enabled
        if request.price_alerts is not None:
            current_preferences.price_alerts = request.price_alerts
        if request.portfolio_updates is not None:
            current_preferences.portfolio_updates = request.portfolio_updates
        if request.market_updates is not None:
            current_preferences.market_updates = request.market_updates
        if request.news_alerts is not None:
            current_preferences.news_alerts = request.news_alerts
        if request.system_alerts is not None:
            current_preferences.system_alerts = request.system_alerts
        if request.backtest_notifications is not None:
            current_preferences.backtest_notifications = request.backtest_notifications
        if request.risk_alerts is not None:
            current_preferences.risk_alerts = request.risk_alerts
        if request.quiet_hours_start is not None:
            current_preferences.quiet_hours_start = request.quiet_hours_start
        if request.quiet_hours_end is not None:
            current_preferences.quiet_hours_end = request.quiet_hours_end
        if request.timezone is not None:
            current_preferences.timezone = request.timezone
        
        # Save updated preferences
        success = notification_service.update_user_preferences(current_user.id, current_preferences)
        
        if success:
            return {
                "message": "Notification preferences updated successfully",
                "user_id": current_user.id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update notification preferences")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

@router.post("/send")
async def send_notification(
    request: SendNotificationRequest,
    current_user = Depends(get_current_user)
):
    """Send a notification to a user"""
    try:
        # Create notification payload
        payload = NotificationPayload(
            title=request.title,
            body=request.body,
            icon=request.icon,
            badge=request.badge,
            image=request.image,
            tag=request.tag,
            data=request.data,
            actions=request.actions,
            require_interaction=request.require_interaction,
            silent=request.silent,
            timestamp=datetime.now()
        )
        
        # Convert notification type
        try:
            notification_type = NotificationType(request.notification_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid notification type")
        
        # Convert channels
        channels = None
        if request.channels:
            channels = []
            for channel_str in request.channels:
                try:
                    channels.append(NotificationChannel(channel_str))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid channel: {channel_str}")
        
        # Send notification
        result = await notification_service.send_notification(
            user_id=request.user_id,
            notification_type=notification_type,
            payload=payload,
            channels=channels
        )
        
        return {
            "message": "Notification sent successfully" if result['sent'] else "Notification failed to send",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.get("/history")
async def get_notification_history(
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """Get user's notification history"""
    try:
        history = notification_service.get_notification_history(current_user.id, limit)
        return {
            "user_id": current_user.id,
            "notifications": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting notification history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification history")

@router.put("/history/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        success = notification_service.mark_notification_read(current_user.id, notification_id)
        
        if success:
            return {
                "message": "Notification marked as read",
                "notification_id": notification_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to mark notification as read")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Get VAPID public key for client-side push subscription"""
    try:
        public_key = notification_service.vapid_public_key
        if public_key:
            return {
                "vapid_public_key": public_key
            }
        else:
            raise HTTPException(status_code=500, detail="VAPID public key not configured")
    except Exception as e:
        logger.error(f"Error getting VAPID public key: {e}")
        raise HTTPException(status_code=500, detail="Failed to get VAPID public key")

@router.post("/test")
async def test_notification(
    current_user = Depends(get_current_user)
):
    """Send a test notification to the current user"""
    try:
        payload = NotificationPayload(
            title="Test Notification",
            body="This is a test notification from Casablanca Insights",
            icon="/icon-192x192.png",
            data={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        result = await notification_service.send_notification(
            user_id=current_user.id,
            notification_type=NotificationType.SYSTEM_ALERT,
            payload=payload
        )
        
        return {
            "message": "Test notification sent",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")

@router.get("/stats")
async def get_notification_stats(current_user = Depends(get_current_user)):
    """Get notification statistics for the user"""
    try:
        # Get user preferences
        preferences = notification_service.get_user_preferences(current_user.id)
        
        # Get subscription count
        subscriptions = notification_service.get_user_subscriptions(current_user.id)
        
        # Get recent notification history
        history = notification_service.get_notification_history(current_user.id, 10)
        
        stats = {
            "user_id": current_user.id,
            "preferences_configured": preferences is not None,
            "push_subscriptions_count": len(subscriptions),
            "recent_notifications_count": len(history),
            "unread_notifications_count": len([n for n in history if not n.get('read', False)]),
            "channels_enabled": {
                "web_push": preferences.web_push_enabled if preferences else False,
                "email": preferences.email_enabled if preferences else False,
                "sms": preferences.sms_enabled if preferences else False,
                "in_app": preferences.in_app_enabled if preferences else False
            } if preferences else {}
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification stats") 