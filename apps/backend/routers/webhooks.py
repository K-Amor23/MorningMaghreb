from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
import hashlib
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["Webhook Integrations"])

# Request/Response Models
class WebhookSubscriptionRequest(BaseModel):
    webhook_url: str
    events: List[str]  # ['price_alert', 'earnings_release', 'dividend_payment', 'macro_update']
    description: Optional[str] = None
    is_active: bool = True

class WebhookSubscriptionResponse(BaseModel):
    id: str
    webhook_url: str
    events: List[str]
    secret_key: str  # Only shown once on creation
    is_active: bool
    delivery_count: int = 0
    failure_count: int = 0
    last_delivery: Optional[datetime] = None
    created_at: datetime

class WebhookDelivery(BaseModel):
    id: str
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    status: str  # 'pending', 'delivered', 'failed'
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    delivery_time_ms: Optional[int] = None
    created_at: datetime

# Mock database functions (replace with actual Supabase calls)
async def get_user_subscription_tier(user_id: str) -> str:
    """Get user's subscription tier"""
    # Mock implementation - replace with actual database query
    return "pro"  # or "institutional"

async def create_webhook_subscription(user_id: str, webhook_data: dict) -> str:
    """Create webhook subscription in database"""
    # Mock implementation - replace with actual database insert
    return "mock_webhook_id"

async def get_webhook_subscriptions(user_id: str) -> List[Dict[str, Any]]:
    """Get user's webhook subscriptions"""
    # Mock implementation - replace with actual database query
    return [
        {
            "id": "webhook_1",
            "webhook_url": "https://hooks.zapier.com/hooks/catch/123456/abc123/",
            "events": ["price_alert", "earnings_release"],
            "is_active": True,
            "delivery_count": 45,
            "failure_count": 2,
            "last_delivery": datetime.utcnow() - timedelta(hours=2),
            "created_at": datetime.utcnow() - timedelta(days=30)
        },
        {
            "id": "webhook_2",
            "webhook_url": "https://hook.eu1.make.com/xyz789",
            "events": ["dividend_payment"],
            "is_active": True,
            "delivery_count": 12,
            "failure_count": 0,
            "last_delivery": datetime.utcnow() - timedelta(days=1),
            "created_at": datetime.utcnow() - timedelta(days=15)
        }
    ]

async def log_webhook_delivery(webhook_id: str, delivery_data: dict):
    """Log webhook delivery attempt"""
    # Mock implementation
    logger.info(f"Webhook delivery logged: {webhook_id}")

# Authentication dependency (mock)
async def get_current_user() -> dict:
    """Get current authenticated user"""
    return {"id": "mock_user_id", "subscription_tier": "pro"}

# Webhook Management
@router.post("/", response_model=WebhookSubscriptionResponse)
async def create_webhook_subscription(
    request: WebhookSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new webhook subscription"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required for webhooks")
        
        # Validate events
        valid_events = ["price_alert", "earnings_release", "dividend_payment", "macro_update", "portfolio_change"]
        for event in request.events:
            if event not in valid_events:
                raise HTTPException(status_code=400, detail=f"Invalid event: {event}. Must be one of: {valid_events}")
        
        # Generate secret key for webhook signature
        secret_key = f"whsec_{secrets.token_urlsafe(32)}"
        
        # Create webhook subscription
        webhook_id = await create_webhook_subscription(user["id"], {
            "webhook_url": request.webhook_url,
            "events": request.events,
            "description": request.description,
            "is_active": request.is_active,
            "secret_key": secret_key
        })
        
        return WebhookSubscriptionResponse(
            id=webhook_id,
            webhook_url=request.webhook_url,
            events=request.events,
            secret_key=secret_key,  # Only shown once
            is_active=request.is_active,
            delivery_count=0,
            failure_count=0,
            last_delivery=None,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error creating webhook subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create webhook subscription")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_webhook_subscriptions(user: dict = Depends(get_current_user)):
    """List user's webhook subscriptions"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        webhooks = await get_webhook_subscriptions(user["id"])
        
        # Don't include secret keys in list response
        for webhook in webhooks:
            if "secret_key" in webhook:
                del webhook["secret_key"]
        
        return webhooks
        
    except Exception as e:
        logger.error(f"Error listing webhook subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list webhook subscriptions")

@router.get("/{webhook_id}", response_model=Dict[str, Any])
async def get_webhook_subscription(
    webhook_id: str,
    user: dict = Depends(get_current_user)
):
    """Get specific webhook subscription details"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Mock webhook details (replace with actual database query)
        webhook = {
            "id": webhook_id,
            "webhook_url": "https://hooks.zapier.com/hooks/catch/123456/abc123/",
            "events": ["price_alert", "earnings_release"],
            "description": "Zapier integration for price alerts",
            "is_active": True,
            "delivery_count": 45,
            "failure_count": 2,
            "last_delivery": datetime.utcnow() - timedelta(hours=2),
            "created_at": datetime.utcnow() - timedelta(days=30),
            "secret_key": "whsec_mock_secret_key"  # Include for individual view
        }
        
        return webhook
        
    except Exception as e:
        logger.error(f"Error getting webhook subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook subscription")

@router.put("/{webhook_id}")
async def update_webhook_subscription(
    webhook_id: str,
    request: WebhookSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """Update webhook subscription"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Validate events
        valid_events = ["price_alert", "earnings_release", "dividend_payment", "macro_update", "portfolio_change"]
        for event in request.events:
            if event not in valid_events:
                raise HTTPException(status_code=400, detail=f"Invalid event: {event}")
        
        # Mock update (replace with actual database update)
        logger.info(f"Webhook {webhook_id} updated")
        
        return {"message": "Webhook subscription updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating webhook subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to update webhook subscription")

@router.delete("/{webhook_id}")
async def delete_webhook_subscription(
    webhook_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete webhook subscription"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Mock deletion (replace with actual database delete)
        logger.info(f"Webhook {webhook_id} deleted")
        
        return {"message": "Webhook subscription deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting webhook subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook subscription")

# Webhook Delivery History
@router.get("/{webhook_id}/deliveries", response_model=List[Dict[str, Any]])
async def get_webhook_deliveries(
    webhook_id: str,
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get webhook delivery history"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Mock delivery history (replace with actual database query)
        deliveries = [
            {
                "id": "delivery_1",
                "webhook_id": webhook_id,
                "event_type": "price_alert",
                "status": "delivered",
                "response_code": 200,
                "delivery_time_ms": 245,
                "created_at": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "delivery_2",
                "webhook_id": webhook_id,
                "event_type": "earnings_release",
                "status": "failed",
                "response_code": 500,
                "response_body": "Internal server error",
                "delivery_time_ms": 5000,
                "created_at": datetime.utcnow() - timedelta(hours=2)
            }
        ]
        
        return deliveries[offset:offset + limit]
        
    except Exception as e:
        logger.error(f"Error getting webhook deliveries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook deliveries")

# Webhook Testing
@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    user: dict = Depends(get_current_user)
):
    """Send a test webhook to verify configuration"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Mock test webhook (replace with actual webhook delivery)
        test_payload = {
            "event_type": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "This is a test webhook from Casablanca Insights",
                "user_id": user["id"],
                "webhook_id": webhook_id
            }
        }
        
        # Simulate webhook delivery
        logger.info(f"Test webhook sent to {webhook_id}")
        
        return {
            "message": "Test webhook sent successfully",
            "payload": test_payload,
            "delivery_time_ms": 150
        }
        
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test webhook")

# Webhook Statistics
@router.get("/stats", response_model=Dict[str, Any])
async def get_webhook_stats(user: dict = Depends(get_current_user)):
    """Get webhook delivery statistics"""
    try:
        # Check subscription tier
        subscription_tier = await get_user_subscription_tier(user["id"])
        if subscription_tier not in ["pro", "institutional"]:
            raise HTTPException(status_code=403, detail="Pro or Institutional tier required")
        
        # Mock statistics (replace with actual database aggregation)
        stats = {
            "total_webhooks": 3,
            "active_webhooks": 2,
            "total_deliveries": 157,
            "successful_deliveries": 145,
            "failed_deliveries": 12,
            "success_rate": 0.92,
            "average_delivery_time_ms": 320,
            "deliveries_by_event": {
                "price_alert": 89,
                "earnings_release": 45,
                "dividend_payment": 23
            },
            "recent_activity": {
                "last_24_hours": 12,
                "last_7_days": 67,
                "last_30_days": 157
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting webhook stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook statistics")

# Webhook Event Types
@router.get("/events", response_model=List[Dict[str, Any]])
async def get_webhook_event_types():
    """Get available webhook event types"""
    try:
        event_types = [
            {
                "event": "price_alert",
                "description": "Triggered when a stock price crosses a specified threshold",
                "payload_example": {
                    "event_type": "price_alert",
                    "ticker": "ATW",
                    "current_price": 150.25,
                    "threshold": 150.00,
                    "direction": "above",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            },
            {
                "event": "earnings_release",
                "description": "Triggered when a company releases earnings",
                "payload_example": {
                    "event_type": "earnings_release",
                    "ticker": "IAM",
                    "company_name": "Maroc Telecom",
                    "earnings_date": "2024-01-15",
                    "estimate": 1.85,
                    "actual": 1.92,
                    "surprise": 0.07
                }
            },
            {
                "event": "dividend_payment",
                "description": "Triggered when a dividend payment is announced",
                "payload_example": {
                    "event_type": "dividend_payment",
                    "ticker": "BCP",
                    "company_name": "Banque Centrale Populaire",
                    "ex_date": "2024-01-20",
                    "payment_date": "2024-01-25",
                    "amount": 8.50,
                    "dividend_yield": 3.8
                }
            },
            {
                "event": "macro_update",
                "description": "Triggered when key macroeconomic indicators are updated",
                "payload_example": {
                    "event_type": "macro_update",
                    "indicator": "CPI",
                    "value": 120.5,
                    "change": 0.3,
                    "date": "2024-01-15",
                    "source": "Bank Al-Maghrib"
                }
            },
            {
                "event": "portfolio_change",
                "description": "Triggered when portfolio value changes significantly",
                "payload_example": {
                    "event_type": "portfolio_change",
                    "portfolio_id": "portfolio_123",
                    "previous_value": 100000,
                    "current_value": 105000,
                    "change_percent": 5.0,
                    "timestamp": "2024-01-15T16:00:00Z"
                }
            }
        ]
        
        return event_types
        
    except Exception as e:
        logger.error(f"Error getting webhook event types: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook event types")

# Webhook Documentation
@router.get("/docs", response_model=Dict[str, Any])
async def get_webhook_documentation():
    """Get webhook integration documentation"""
    try:
        docs = {
            "overview": "Webhooks allow you to receive real-time notifications from Casablanca Insights when specific events occur.",
            "authentication": {
                "method": "HMAC-SHA256 signature",
                "header": "X-Casablanca-Signature",
                "description": "Each webhook request includes a signature header for verification"
            },
            "rate_limits": {
                "free_tier": "Not available",
                "pro_tier": "100 webhooks per hour",
                "institutional_tier": "1000 webhooks per hour"
            },
            "retry_policy": {
                "max_retries": 3,
                "retry_delays": [5, 30, 300],  # seconds
                "backoff_strategy": "exponential"
            },
            "security": {
                "https_required": True,
                "ip_whitelist": "Optional",
                "secret_verification": "Required"
            },
            "integration_examples": {
                "zapier": "https://zapier.com/apps/morningmaghreb",
"make": "https://www.make.com/en/help/apps/morningmaghreb",
                "custom": "Use any HTTP client that supports webhooks"
            }
        }
        
        return docs
        
    except Exception as e:
        logger.error(f"Error getting webhook documentation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook documentation") 