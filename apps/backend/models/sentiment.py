from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database.database import Base

class SentimentVote(Base):
    __tablename__ = "sentiment_votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ticker = Column(String(10), nullable=False)
    sentiment = Column(String(20), nullable=False)  # "bullish", "neutral", "bearish"
    confidence = Column(Integer, nullable=False, default=1)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sentiment_votes")
    
    class Config:
        orm_mode = True

class SentimentAggregate(Base):
    __tablename__ = "sentiment_aggregates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(10), nullable=False, unique=True)
    bullish_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    bearish_count = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    bullish_percentage = Column(Float, default=0.0)
    neutral_percentage = Column(Float, default=0.0)
    bearish_percentage = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    class Config:
        orm_mode = True 