from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from models.sentiment import SentimentVote, SentimentAggregate
from lib.auth import get_current_user

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

class SentimentVoteRequest(BaseModel):
    ticker: str
    sentiment: str  # "bullish", "neutral", "bearish"
    confidence: Optional[int] = 1  # 1-5 scale

class SentimentVoteResponse(BaseModel):
    id: str
    ticker: str
    sentiment: str
    confidence: int
    user_id: str
    created_at: datetime

class SentimentAggregateResponse(BaseModel):
    ticker: str
    bullish_count: int
    neutral_count: int
    bearish_count: int
    total_votes: int
    bullish_percentage: float
    neutral_percentage: float
    bearish_percentage: float
    average_confidence: float
    last_updated: datetime

@router.post("/vote", response_model=SentimentVoteResponse)
async def vote_sentiment(
    vote: SentimentVoteRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on stock sentiment (bullish/neutral/bearish)
    """
    if vote.sentiment not in ["bullish", "neutral", "bearish"]:
        raise HTTPException(status_code=400, detail="Invalid sentiment. Must be bullish, neutral, or bearish")
    
    if vote.confidence < 1 or vote.confidence > 5:
        raise HTTPException(status_code=400, detail="Confidence must be between 1 and 5")
    
    # Check if user already voted on this ticker
    existing_vote = db.query(SentimentVote).filter(
        SentimentVote.user_id == current_user.id,
        SentimentVote.ticker == vote.ticker
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.sentiment = vote.sentiment
        existing_vote.confidence = vote.confidence
        existing_vote.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_vote)
        
        # Update aggregate
        update_sentiment_aggregate(vote.ticker, db)
        
        return SentimentVoteResponse(
            id=str(existing_vote.id),
            ticker=existing_vote.ticker,
            sentiment=existing_vote.sentiment,
            confidence=existing_vote.confidence,
            user_id=str(existing_vote.user_id),
            created_at=existing_vote.created_at
        )
    else:
        # Create new vote
        new_vote = SentimentVote(
            user_id=current_user.id,
            ticker=vote.ticker,
            sentiment=vote.sentiment,
            confidence=vote.confidence,
            created_at=datetime.utcnow()
        )
        
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        
        # Update aggregate
        update_sentiment_aggregate(vote.ticker, db)
        
        return SentimentVoteResponse(
            id=str(new_vote.id),
            ticker=new_vote.ticker,
            sentiment=new_vote.sentiment,
            confidence=new_vote.confidence,
            user_id=str(new_vote.user_id),
            created_at=new_vote.created_at
        )

@router.get("/my-votes", response_model=List[SentimentVoteResponse])
async def get_my_votes(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's sentiment votes
    """
    votes = db.query(SentimentVote).filter(
        SentimentVote.user_id == current_user.id
    ).order_by(SentimentVote.created_at.desc()).all()
    
    return [
        SentimentVoteResponse(
            id=str(vote.id),
            ticker=vote.ticker,
            sentiment=vote.sentiment,
            confidence=vote.confidence,
            user_id=str(vote.user_id),
            created_at=vote.created_at
        )
        for vote in votes
    ]

@router.get("/aggregate/{ticker}", response_model=SentimentAggregateResponse)
async def get_sentiment_aggregate(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Get aggregate sentiment for a specific ticker
    """
    aggregate = db.query(SentimentAggregate).filter(
        SentimentAggregate.ticker == ticker
    ).first()
    
    if not aggregate:
        # Create empty aggregate if none exists
        aggregate = SentimentAggregate(
            ticker=ticker,
            bullish_count=0,
            neutral_count=0,
            bearish_count=0,
            total_votes=0,
            bullish_percentage=0.0,
            neutral_percentage=0.0,
            bearish_percentage=0.0,
            average_confidence=0.0,
            last_updated=datetime.utcnow()
        )
    
    return SentimentAggregateResponse(
        ticker=aggregate.ticker,
        bullish_count=aggregate.bullish_count,
        neutral_count=aggregate.neutral_count,
        bearish_count=aggregate.bearish_count,
        total_votes=aggregate.total_votes,
        bullish_percentage=aggregate.bullish_percentage,
        neutral_percentage=aggregate.neutral_percentage,
        bearish_percentage=aggregate.bearish_percentage,
        average_confidence=aggregate.average_confidence,
        last_updated=aggregate.last_updated
    )

@router.get("/top-sentiment", response_model=List[SentimentAggregateResponse])
async def get_top_sentiment_stocks(
    sentiment_type: str = "bullish",  # "bullish", "neutral", "bearish"
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get top stocks by sentiment type
    """
    if sentiment_type not in ["bullish", "neutral", "bearish"]:
        raise HTTPException(status_code=400, detail="Invalid sentiment type")
    
    # Order by the specific sentiment count
    order_column = getattr(SentimentAggregate, f"{sentiment_type}_count")
    
    aggregates = db.query(SentimentAggregate).filter(
        SentimentAggregate.total_votes >= 5  # Minimum votes threshold
    ).order_by(order_column.desc()).limit(limit).all()
    
    return [
        SentimentAggregateResponse(
            ticker=agg.ticker,
            bullish_count=agg.bullish_count,
            neutral_count=agg.neutral_count,
            bearish_count=agg.bearish_count,
            total_votes=agg.total_votes,
            bullish_percentage=agg.bullish_percentage,
            neutral_percentage=agg.neutral_percentage,
            bearish_percentage=agg.bearish_percentage,
            average_confidence=agg.average_confidence,
            last_updated=agg.last_updated
        )
        for agg in aggregates
    ]

@router.delete("/vote/{ticker}")
async def delete_sentiment_vote(
    ticker: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user's sentiment vote for a ticker
    """
    vote = db.query(SentimentVote).filter(
        SentimentVote.user_id == current_user.id,
        SentimentVote.ticker == ticker
    ).first()
    
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    db.delete(vote)
    db.commit()
    
    # Update aggregate
    update_sentiment_aggregate(ticker, db)
    
    return {"message": "Vote deleted successfully"}

def update_sentiment_aggregate(ticker: str, db: Session):
    """
    Update sentiment aggregate for a ticker
    """
    # Get all votes for the ticker
    votes = db.query(SentimentVote).filter(SentimentVote.ticker == ticker).all()
    
    if not votes:
        # Remove aggregate if no votes
        db.query(SentimentAggregate).filter(
            SentimentAggregate.ticker == ticker
        ).delete()
        db.commit()
        return
    
    # Calculate aggregates
    total_votes = len(votes)
    bullish_count = len([v for v in votes if v.sentiment == "bullish"])
    neutral_count = len([v for v in votes if v.sentiment == "neutral"])
    bearish_count = len([v for v in votes if v.sentiment == "bearish"])
    
    bullish_percentage = (bullish_count / total_votes) * 100 if total_votes > 0 else 0
    neutral_percentage = (neutral_count / total_votes) * 100 if total_votes > 0 else 0
    bearish_percentage = (bearish_count / total_votes) * 100 if total_votes > 0 else 0
    
    average_confidence = sum(v.confidence for v in votes) / total_votes if total_votes > 0 else 0
    
    # Update or create aggregate
    aggregate = db.query(SentimentAggregate).filter(
        SentimentAggregate.ticker == ticker
    ).first()
    
    if aggregate:
        aggregate.bullish_count = bullish_count
        aggregate.neutral_count = neutral_count
        aggregate.bearish_count = bearish_count
        aggregate.total_votes = total_votes
        aggregate.bullish_percentage = bullish_percentage
        aggregate.neutral_percentage = neutral_percentage
        aggregate.bearish_percentage = bearish_percentage
        aggregate.average_confidence = average_confidence
        aggregate.last_updated = datetime.utcnow()
    else:
        aggregate = SentimentAggregate(
            ticker=ticker,
            bullish_count=bullish_count,
            neutral_count=neutral_count,
            bearish_count=bearish_count,
            total_votes=total_votes,
            bullish_percentage=bullish_percentage,
            neutral_percentage=neutral_percentage,
            bearish_percentage=bearish_percentage,
            average_confidence=average_confidence,
            last_updated=datetime.utcnow()
        )
        db.add(aggregate)
    
    db.commit() 