from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..models.moderation import (
    ModerationRequest, ModerationResponse, ContentType, 
    CulturalGuideline, ModerationLog, SafeContentTemplate
)
from ..lib.ai_moderation import moderation_service
from ..lib.database import get_db
from ..lib.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderation", tags=["moderation"])

@router.post("/check", response_model=ModerationResponse)
async def check_content(
    request: ModerationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check content for cultural sensitivity and provide moderation"""
    try:
        # Perform content moderation
        response = moderation_service.moderate_content(request)
        
        # Log the moderation request
        log_entry = ModerationLog(
            user_id=current_user.id if current_user else None,
            content_type=request.content_type,
            original_length=len(request.text),
            moderation_level=response.moderation_level,
            processing_time_ms=0  # Would be calculated in production
        )
        
        # In production, save log to database
        logger.info(f"Content moderation completed for user {current_user.id if current_user else 'anonymous'}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in content moderation: {e}")
        raise HTTPException(status_code=500, detail="Error processing content moderation")

@router.post("/moderate", response_model=ModerationResponse)
async def moderate_content(
    request: ModerationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Moderate content and return safe version"""
    try:
        # Perform content moderation
        response = moderation_service.moderate_content(request)
        
        # If content is blocked, return error
        if response.moderation_level.value == "blocked":
            raise HTTPException(
                status_code=400, 
                detail="Content contains sensitive topics and cannot be processed"
            )
        
        # If content requires review, return warning
        if response.moderation_level.value == "requires_review":
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Content requires manual review",
                    "sensitive_topics": response.sensitive_topics,
                    "suggestions": response.suggestions
                }
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in content moderation: {e}")
        raise HTTPException(status_code=500, detail="Error processing content moderation")

@router.get("/guidelines", response_model=List[CulturalGuideline])
async def get_cultural_guidelines(
    topic: Optional[str] = Query(None, description="Filter by specific topic"),
    db: Session = Depends(get_db)
):
    """Get cultural guidelines for content creation"""
    try:
        # Mock guidelines - in production, fetch from database
        mock_guidelines = [
            CulturalGuideline(
                id="1",
                topic="monarchy",
                guideline_text="Avoid any references to the monarchy, royal family, or royal institutions",
                do_not_mention=["king", "monarch", "royal", "palace", "HM", "His Majesty"],
                preferred_phrasing=["leadership", "institution", "official"],
                severity_level=5
            ),
            CulturalGuideline(
                id="2",
                topic="government",
                guideline_text="Focus on business and economic aspects rather than government activities",
                do_not_mention=["government", "ministry", "minister", "parliament"],
                preferred_phrasing=["authorities", "department", "official"],
                severity_level=4
            ),
            CulturalGuideline(
                id="3",
                topic="religion",
                guideline_text="Keep content secular and business-focused",
                do_not_mention=["Islam", "Muslim", "mosque", "halal", "haram"],
                preferred_phrasing=["business", "commercial", "professional"],
                severity_level=3
            ),
            CulturalGuideline(
                id="4",
                topic="politics",
                guideline_text="Avoid political commentary or analysis",
                do_not_mention=["political", "party", "election", "vote", "opposition"],
                preferred_phrasing=["business environment", "economic factors", "market conditions"],
                severity_level=4
            )
        ]
        
        if topic:
            mock_guidelines = [g for g in mock_guidelines if g.topic == topic]
        
        return mock_guidelines
        
    except Exception as e:
        logger.error(f"Error fetching cultural guidelines: {e}")
        raise HTTPException(status_code=500, detail="Error fetching guidelines")

@router.get("/templates/{content_type}", response_model=SafeContentTemplate)
async def get_safe_template(
    content_type: ContentType,
    db: Session = Depends(get_db)
):
    """Get safe content template for specific content type"""
    try:
        template_text = moderation_service.get_safe_template(content_type)
        
        template = SafeContentTemplate(
            id="1",
            content_type=content_type,
            template_name=f"Safe {content_type.value.replace('_', ' ').title()} Template",
            template_text=template_text,
            variables=["date", "company_name", "revenue", "net_income", "metrics"],
            is_active=True
        )
        
        return template
        
    except Exception as e:
        logger.error(f"Error fetching safe template: {e}")
        raise HTTPException(status_code=500, detail="Error fetching template")

@router.get("/logs", response_model=List[ModerationLog])
async def get_moderation_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    limit: int = Query(50, description="Number of logs to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get moderation logs (admin only)"""
    try:
        # Mock logs - in production, fetch from database with filters
        mock_logs = [
            ModerationLog(
                id="1",
                user_id=current_user.id if current_user else None,
                content_type=ContentType.MARKET_SUMMARY,
                original_length=150,
                moderation_level="safe",
                processing_time_ms=45
            ),
            ModerationLog(
                id="2",
                user_id=current_user.id if current_user else None,
                content_type=ContentType.COMPANY_ANALYSIS,
                original_length=300,
                moderation_level="flagged",
                processing_time_ms=67
            )
        ]
        
        return mock_logs[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching moderation logs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching logs")

@router.post("/test")
async def test_moderation(
    text: str = Query(..., description="Text to test"),
    content_type: ContentType = Query(ContentType.MARKET_SUMMARY, description="Content type"),
    db: Session = Depends(get_db)
):
    """Test moderation with sample text"""
    try:
        request = ModerationRequest(
            content_type=content_type,
            text=text
        )
        
        response = moderation_service.moderate_content(request)
        
        return {
            "original_text": text,
            "moderation_result": response,
            "safe_alternatives": moderation_service.safe_alternatives
        }
        
    except Exception as e:
        logger.error(f"Error in test moderation: {e}")
        raise HTTPException(status_code=500, detail="Error testing moderation") 