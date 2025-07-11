from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID
from enum import Enum

class ContentType(str, Enum):
    MARKET_SUMMARY = "market_summary"
    COMPANY_ANALYSIS = "company_analysis"
    NEWS_DIGEST = "news_digest"
    REPORT_SUMMARY = "report_summary"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

class ModerationLevel(str, Enum):
    SAFE = "safe"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    REQUIRES_REVIEW = "requires_review"

class SensitiveTopic(str, Enum):
    MONARCHY = "monarchy"
    GOVERNMENT = "government"
    RELIGION = "religion"
    POLITICS = "politics"
    CULTURAL_VALUES = "cultural_values"
    ECONOMIC_POLICY = "economic_policy"

class ContentModeration(BaseModel):
    id: Optional[UUID] = None
    content_type: ContentType
    original_text: str
    moderated_text: Optional[str] = None
    moderation_level: ModerationLevel
    sensitive_topics: List[SensitiveTopic] = []
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    flagged_phrases: List[str] = []
    replacement_suggestions: Dict[str, str] = {}
    moderation_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    moderated_at: Optional[datetime] = None

class ModerationRequest(BaseModel):
    content_type: ContentType
    text: str
    context: Optional[str] = None
    user_id: Optional[UUID] = None

class ModerationResponse(BaseModel):
    is_safe: bool
    moderation_level: ModerationLevel
    moderated_text: Optional[str] = None
    sensitive_topics: List[SensitiveTopic] = []
    confidence_score: float
    flagged_phrases: List[str] = []
    suggestions: List[str] = []
    can_proceed: bool

class CulturalGuideline(BaseModel):
    id: Optional[UUID] = None
    topic: SensitiveTopic
    guideline_text: str
    do_not_mention: List[str] = []
    preferred_phrasing: List[str] = []
    severity_level: int = Field(..., ge=1, le=5)  # 1=low, 5=critical
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ModerationLog(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    content_type: ContentType
    original_length: int
    moderation_level: ModerationLevel
    processing_time_ms: int
    created_at: Optional[datetime] = None

class SafeContentTemplate(BaseModel):
    id: Optional[UUID] = None
    content_type: ContentType
    template_name: str
    template_text: str
    variables: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime] = None 