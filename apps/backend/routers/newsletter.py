from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import json
from datetime import datetime, timedelta
import openai
from pydantic import BaseModel
import os
from sqlalchemy.orm import Session
from database.database import get_db
from models.newsletter import NewsletterCampaign, NewsletterSubscriber
from lib.openai_service import generate_weekly_recap

router = APIRouter(tags=["newsletter"])

class WeeklyRecapRequest(BaseModel):
    include_macro: bool = True
    include_sectors: bool = True
    include_top_movers: bool = True
    language: str = "en"  # en, fr, ar

class NewsletterResponse(BaseModel):
    id: str
    subject: str
    content: str
    sent_at: Optional[datetime]
    recipient_count: Optional[int]
    open_count: int = 0
    click_count: int = 0

@router.post("/generate-weekly-recap", response_model=NewsletterResponse)
async def generate_weekly_market_recap(
    request: WeeklyRecapRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered weekly market recap newsletter
    """
    try:
        # Generate the weekly recap content using AI
        recap_content = await generate_weekly_recap(
            include_macro=request.include_macro,
            include_sectors=request.include_sectors,
            include_top_movers=request.include_top_movers,
            language=request.language
        )
        
        # Create newsletter campaign (mock for now since we don't have a real database)
        campaign_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # For now, return the content directly without database storage
        return NewsletterResponse(
            id=campaign_id,
            subject=recap_content["subject"],
            content=recap_content["content"],
            sent_at=None,
            recipient_count=None
        )
        
        # Note: Background sending is disabled for now since we don't have a real database
        # background_tasks.add_task(send_weekly_recap, campaign_id, db)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly recap: {str(e)}")

@router.post("/weekly-recap/preview")
async def preview_weekly_recap(
    request: WeeklyRecapRequest,
    db: Session = Depends(get_db)
):
    """
    Preview the weekly recap without sending
    """
    try:
        recap_content = await generate_weekly_recap(
            include_macro=request.include_macro,
            include_sectors=request.include_sectors,
            include_top_movers=request.include_top_movers,
            language=request.language
        )
        
        return {
            "subject": recap_content["subject"],
            "content": recap_content["content"],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

@router.get("/subscribers", response_model=List[dict])
async def get_newsletter_subscribers(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get newsletter subscribers with optional status filter
    """
    query = db.query(NewsletterSubscriber)
    
    if status:
        query = query.filter(NewsletterSubscriber.status == status)
    
    subscribers = query.all()
    
    return [
        {
            "id": str(sub.id),
            "email": sub.email,
            "name": sub.name,
            "status": sub.status,
            "subscribed_at": sub.subscribed_at.isoformat(),
            "preferences": sub.preferences
        }
        for sub in subscribers
    ]

@router.post("/send-test")
async def send_test_newsletter(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Send a test weekly recap to a specific email
    """
    try:
        # Generate test recap
        recap_content = await generate_weekly_recap(
            include_macro=True,
            include_sectors=True,
            include_top_movers=True,
            language="en"
        )
        
        # Send test email
        from lib.email_service import send_email
        result = await send_email(
            to_email=email,
            subject=f"[TEST] {recap_content['subject']}",
            content=recap_content["content"]
        )
        
        if result["success"]:
            return {"message": f"Test newsletter sent to {email}", "provider": result["provider"]}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {result['message']}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test: {str(e)}")

@router.get("/stats")
async def get_newsletter_stats(db: Session = Depends(get_db)):
    """
    Get newsletter statistics
    """
    try:
        # Mock stats for now
        stats = {
            "total_subscribers": 0,
            "active_subscribers": 0,
            "total_campaigns": 0,
            "campaigns_sent": 0,
            "total_emails_sent": 0,
            "open_rate": 0.0,
            "click_rate": 0.0
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/campaigns")
async def get_newsletter_campaigns(db: Session = Depends(get_db)):
    """
    Get newsletter campaigns
    """
    try:
        # Mock campaigns for now
        campaigns = []
        
        return campaigns
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns: {str(e)}")

@router.get("/content")
async def get_newsletter_content(db: Session = Depends(get_db)):
    """
    Get generated newsletter content
    """
    try:
        # Mock content for now
        content = []
        
        return content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

async def send_weekly_recap(campaign_id: str, db: Session):
    """
    Background task to send weekly recap to all subscribers
    """
    try:
        campaign = db.query(NewsletterCampaign).filter(
            NewsletterCampaign.id == campaign_id
        ).first()
        
        if not campaign:
            return
        
        # Get active subscribers
        subscribers = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.status == "active"
        ).all()
        
        # Send emails
        from lib.email_service import send_bulk_email
        await send_bulk_email(
            subscribers=[sub.email for sub in subscribers],
            subject=campaign.subject,
            content=campaign.content
        )
        
        # Update campaign stats
        campaign.sent_at = datetime.utcnow()
        campaign.recipient_count = len(subscribers)
        db.commit()
        
    except Exception as e:
        print(f"Error sending weekly recap: {str(e)}") 