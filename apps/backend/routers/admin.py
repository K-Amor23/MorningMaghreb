from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Mock data - replace with actual database queries
def get_mock_users():
    return [
        {
            "id": "1",
            "name": "John Doe",
            "email": "john@example.com",
            "role": "premium",
            "status": "active",
            "joinedAt": "2024-01-15T10:00:00Z",
            "lastActive": "2024-01-25T10:00:00Z",
            "newsletterSubscribed": True,
            "paperTradingAccount": True
        },
        {
            "id": "2",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "role": "user",
            "status": "active",
            "joinedAt": "2024-01-20T10:00:00Z",
            "lastActive": "2024-01-24T10:00:00Z",
            "newsletterSubscribed": False,
            "paperTradingAccount": False
        },
        {
            "id": "3",
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "role": "premium",
            "status": "inactive",
            "joinedAt": "2024-01-10T10:00:00Z",
            "lastActive": "2024-01-18T10:00:00Z",
            "newsletterSubscribed": True,
            "paperTradingAccount": True
        }
    ]

def get_mock_newsletter_subscribers():
    return [
        {
            "id": "1",
            "email": "john@example.com",
            "status": "active",
            "subscribedAt": "2024-01-15T10:00:00Z",
            "lastEmailSent": "2025-07-25T10:00:00Z",
            "language": "en"
        },
        {
            "id": "2",
            "email": "jane@example.com",
            "status": "active",
            "subscribedAt": "2024-01-20T10:00:00Z",
            "lastEmailSent": "2025-07-25T10:00:00Z",
            "language": "fr"
        },
        {
            "id": "3",
            "email": "bob@example.com",
            "status": "unsubscribed",
            "subscribedAt": "2024-01-10T10:00:00Z",
            "lastEmailSent": "2025-07-18T10:00:00Z",
            "language": "en"
        }
    ]

def get_mock_newsletter_campaigns():
    return [
        {
            "id": "1",
            "subject": "Morocco Markets Weekly Recap - July 25, 2025",
            "status": "sent",
            "recipientCount": 2341,
            "openRate": 68.5,
            "clickRate": 12.3,
            "sentAt": "2025-07-25T10:00:00Z",
            "language": "en"
        },
        {
            "id": "2",
            "subject": "Récapitulatif Hebdomadaire des Marchés Marocains",
            "status": "scheduled",
            "recipientCount": 1890,
            "openRate": 0,
            "clickRate": 0,
            "scheduledFor": "2025-07-26T10:00:00Z",
            "language": "fr"
        },
        {
            "id": "3",
            "subject": "ملخص أسبوعي للأسواق المغربية",
            "status": "draft",
            "recipientCount": 0,
            "openRate": 0,
            "clickRate": 0,
            "language": "ar"
        }
    ]

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard overview statistics"""
    users = get_mock_users()
    subscribers = get_mock_newsletter_subscribers()
    campaigns = get_mock_newsletter_campaigns()
    
    return {
        "totalUsers": len(users),
        "activeUsers": len([u for u in users if u["status"] == "active"]),
        "premiumUsers": len([u for u in users if u["role"] == "premium"]),
        "newsletterSubscribers": len(subscribers),
        "paperTradingAccounts": len([u for u in users if u["paperTradingAccount"]]),
        "activeTraders": len([u for u in users if u["paperTradingAccount"] and u["status"] == "active"]),
        "monthlyRevenue": 12450,
        "userGrowth": 12.5,
        "newsletterGrowth": 8.3,
        "tradingGrowth": 15.7
    }

@router.get("/users")
async def get_users(
    search: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None
):
    """Get users with optional filtering"""
    users = get_mock_users()
    
    # Apply filters
    if search:
        users = [u for u in users if 
                search.lower() in u["name"].lower() or 
                search.lower() in u["email"].lower()]
    
    if status and status != "all":
        users = [u for u in users if u["status"] == status]
    
    if role and role != "all":
        users = [u for u in users if u["role"] == role]
    
    return {
        "users": users,
        "total": len(users)
    }

@router.get("/newsletter/subscribers")
async def get_newsletter_subscribers():
    """Get newsletter subscribers"""
    subscribers = get_mock_newsletter_subscribers()
    
    return {
        "subscribers": subscribers,
        "total": len(subscribers),
        "active": len([s for s in subscribers if s["status"] == "active"])
    }

@router.get("/newsletter/campaigns")
async def get_newsletter_campaigns():
    """Get newsletter campaigns"""
    campaigns = get_mock_newsletter_campaigns()
    
    return {
        "campaigns": campaigns,
        "total": len(campaigns),
        "sent": len([c for c in campaigns if c["status"] == "sent"]),
        "scheduled": len([c for c in campaigns if c["status"] == "scheduled"]),
        "draft": len([c for c in campaigns if c["status"] == "draft"])
    }

@router.get("/paper-trading/accounts")
async def get_paper_trading_accounts():
    """Get paper trading accounts and performance"""
    # Mock data for paper trading accounts
    accounts = [
        {
            "id": "1",
            "userId": "1",
            "userName": "John Doe",
            "balance": 125000,
            "totalReturn": 12.5,
            "activePositions": 8,
            "lastTrade": "2024-01-25T10:00:00Z",
            "status": "active"
        },
        {
            "id": "2",
            "userId": "3",
            "userName": "Bob Johnson",
            "balance": 89000,
            "totalReturn": -2.3,
            "activePositions": 3,
            "lastTrade": "2024-01-24T10:00:00Z",
            "status": "active"
        }
    ]
    
    return {
        "accounts": accounts,
        "total": len(accounts),
        "active": len([a for a in accounts if a["status"] == "active"]),
        "totalBalance": sum(a["balance"] for a in accounts),
        "averageReturn": sum(a["totalReturn"] for a in accounts) / len(accounts) if accounts else 0
    }

@router.get("/system/status")
async def get_system_status():
    """Get system monitoring status"""
    return {
        "apiStatus": "healthy",
        "databaseStatus": "connected",
        "openaiStatus": "connected",
        "lastDataRefresh": "2024-01-25T10:00:00Z",
        "uptime": "99.9%",
        "activeUsers": 45,
        "errorCount": 0
    }

@router.post("/newsletter/export-subscribers")
async def export_newsletter_subscribers():
    """Export newsletter subscribers as CSV"""
    subscribers = get_mock_newsletter_subscribers()
    
    # Generate CSV content
    csv_content = "Email,Status,Subscribed,Language\n"
    for subscriber in subscribers:
        csv_content += f"{subscriber['email']},{subscriber['status']},{subscriber['subscribedAt']},{subscriber['language']}\n"
    
    return {
        "csv": csv_content,
        "filename": f"newsletter_subscribers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    } 