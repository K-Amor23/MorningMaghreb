from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import asyncio
import json

from pydantic import BaseModel
from utils.auth import get_current_user

router = APIRouter(prefix="/news-analysis", tags=["news-analysis"])

class NewsLanguage(str, Enum):
    ARABIC = "ar"
    FRENCH = "fr"
    ENGLISH = "en"

class SentimentScore(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class NewsSource(BaseModel):
    name: str
    url: str
    language: NewsLanguage
    reliability_score: Decimal  # 0-100
    last_updated: datetime

class NewsArticle(BaseModel):
    id: str
    title: str
    title_ar: Optional[str] = None
    content: str
    content_ar: Optional[str] = None
    source: str
    source_url: str
    language: NewsLanguage
    published_at: datetime
    companies_mentioned: List[str]
    sectors_mentioned: List[str]
    sentiment_score: Decimal  # -1 to 1
    sentiment_label: SentimentScore
    impact_score: Decimal  # 0-100
    is_breaking: bool = False

class NewsSummary(BaseModel):
    article_id: str
    summary_en: str
    summary_ar: str
    key_points: List[str]
    market_impact: str
    affected_companies: List[str]
    confidence_score: Decimal  # 0-100
    generated_at: datetime

class SentimentAnalysis(BaseModel):
    article_id: str
    overall_sentiment: SentimentScore
    sentiment_score: Decimal  # -1 to 1
    confidence: Decimal  # 0-100
    emotions: Dict[str, Decimal]  # joy, anger, fear, surprise, etc.
    market_implications: List[str]
    analyzed_at: datetime

class SectorSentiment(BaseModel):
    sector: str
    sector_ar: str
    sentiment_score: Decimal  # -1 to 1
    sentiment_label: SentimentScore
    change_24h: Decimal
    article_count: int
    volume_indicator: str  # low, medium, high
    last_updated: datetime

class CompanyNewsImpact(BaseModel):
    ticker: str
    company_name: str
    impact_score: Decimal  # 0-100
    sentiment_score: Decimal  # -1 to 1
    news_count: int
    latest_news: List[NewsArticle]
    impact_type: str  # positive, negative, neutral
    urgency: str  # low, medium, high

class PortfolioNewsAlert(BaseModel):
    id: str
    user_id: str
    portfolio_id: str
    article_id: str
    ticker: str
    impact_score: Decimal
    alert_type: str  # price_impact, sentiment_change, breaking_news
    message: str
    sent_at: datetime
    is_read: bool = False

class NewsHeatmap(BaseModel):
    sectors: List[SectorSentiment]
    companies: List[CompanyNewsImpact]
    market_mood: str  # optimistic, cautious, pessimistic
    volatility_indicator: str  # low, medium, high
    generated_at: datetime

# Mock data storage
mock_news_articles = {}
mock_news_summaries = {}
mock_sentiment_analysis = {}
mock_portfolio_alerts = {}

@router.get("/articles", response_model=List[NewsArticle])
async def get_news_articles(
    limit: int = Query(20, ge=1, le=100),
    language: Optional[NewsLanguage] = Query(None),
    sentiment: Optional[SentimentScore] = Query(None),
    company: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),  # Last N hours
    current_user = Depends(get_current_user)
):
    """Get financial news articles with filtering options"""
    try:
        # Generate mock articles if none exist
        if not mock_news_articles:
            await generate_mock_news_articles()
        
        # Filter articles
        articles = list(mock_news_articles.values())
        
        # Time filter
        cutoff_time = datetime.now() - timedelta(hours=hours)
        articles = [a for a in articles if a.published_at >= cutoff_time]
        
        # Language filter
        if language:
            articles = [a for a in articles if a.language == language]
        
        # Sentiment filter
        if sentiment:
            articles = [a for a in articles if a.sentiment_label == sentiment]
        
        # Company filter
        if company:
            articles = [a for a in articles if company.upper() in a.companies_mentioned]
        
        # Sector filter
        if sector:
            articles = [a for a in articles if sector.lower() in [s.lower() for s in a.sectors_mentioned]]
        
        # Sort by published date (newest first)
        articles.sort(key=lambda x: x.published_at, reverse=True)
        
        return articles[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news articles: {str(e)}")

@router.post("/articles/{article_id}/summarize", response_model=NewsSummary)
async def summarize_article(
    article_id: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Generate AI-powered summary of a news article"""
    try:
        if article_id not in mock_news_articles:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article = mock_news_articles[article_id]
        
        # Check if summary already exists
        if article_id in mock_news_summaries:
            return mock_news_summaries[article_id]
        
        # Generate summary using AI (mock implementation)
        summary = await generate_ai_summary(article)
        
        # Store summary
        mock_news_summaries[article_id] = summary
        
        # Schedule background task to update related alerts
        background_tasks.add_task(update_portfolio_alerts, article, current_user.id)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing article: {str(e)}")

@router.get("/sentiment-analysis/{article_id}", response_model=SentimentAnalysis)
async def analyze_article_sentiment(
    article_id: str,
    current_user = Depends(get_current_user)
):
    """Analyze sentiment of a news article"""
    try:
        if article_id not in mock_news_articles:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article = mock_news_articles[article_id]
        
        # Check if analysis already exists
        if article_id in mock_sentiment_analysis:
            return mock_sentiment_analysis[article_id]
        
        # Perform sentiment analysis
        sentiment_analysis = await perform_sentiment_analysis(article)
        
        # Store analysis
        mock_sentiment_analysis[article_id] = sentiment_analysis
        
        return sentiment_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.get("/sector-sentiment", response_model=List[SectorSentiment])
async def get_sector_sentiment(
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(get_current_user)
):
    """Get sentiment analysis by sector"""
    try:
        # Define Moroccan market sectors
        sectors = {
            "banking": "المصرفية",
            "telecommunications": "الاتصالات",
            "mining": "التعدين",
            "energy": "الطاقة",
            "real_estate": "العقارات",
            "agriculture": "الزراعة",
            "tourism": "السياحة",
            "automotive": "السيارات",
            "pharmaceuticals": "الصناعات الدوائية",
            "textiles": "النسيج"
        }
        
        sector_sentiments = []
        
        for sector_en, sector_ar in sectors.items():
            # Calculate sector sentiment (mock implementation)
            sentiment_score = await calculate_sector_sentiment(sector_en, hours)
            sentiment_label = get_sentiment_label(sentiment_score)
            
            sector_sentiment = SectorSentiment(
                sector=sector_en,
                sector_ar=sector_ar,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                change_24h=Decimal(str(sentiment_score * 0.1)),  # Mock change
                article_count=await count_sector_articles(sector_en, hours),
                volume_indicator=get_volume_indicator(sector_en),
                last_updated=datetime.now()
            )
            
            sector_sentiments.append(sector_sentiment)
        
        # Sort by sentiment score (most positive first)
        sector_sentiments.sort(key=lambda x: x.sentiment_score, reverse=True)
        
        return sector_sentiments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector sentiment: {str(e)}")

@router.get("/company-impact", response_model=List[CompanyNewsImpact])
async def get_company_news_impact(
    tickers: Optional[str] = Query(None, description="Comma-separated list of tickers"),
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(get_current_user)
):
    """Get news impact analysis for companies"""
    try:
        # Default to major Moroccan companies if no tickers specified
        if tickers:
            ticker_list = [t.strip().upper() for t in tickers.split(",")]
        else:
            ticker_list = ["ATW", "IAM", "BCP", "OCP", "BMCE", "CMT", "LAFA", "CIH", "MNG", "TMA"]
        
        company_impacts = []
        
        for ticker in ticker_list:
            impact = await calculate_company_news_impact(ticker, hours)
            company_impacts.append(impact)
        
        # Sort by impact score (highest first)
        company_impacts.sort(key=lambda x: x.impact_score, reverse=True)
        
        return company_impacts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company news impact: {str(e)}")

@router.get("/portfolio-alerts", response_model=List[PortfolioNewsAlert])
async def get_portfolio_news_alerts(
    portfolio_id: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get news alerts for user's portfolio"""
    try:
        # Filter alerts by user
        user_alerts = [
            alert for alert in mock_portfolio_alerts.values()
            if alert.user_id == current_user.id
        ]
        
        # Filter by portfolio if specified
        if portfolio_id:
            user_alerts = [a for a in user_alerts if a.portfolio_id == portfolio_id]
        
        # Filter by read status
        if unread_only:
            user_alerts = [a for a in user_alerts if not a.is_read]
        
        # Sort by sent date (newest first)
        user_alerts.sort(key=lambda x: x.sent_at, reverse=True)
        
        return user_alerts[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio alerts: {str(e)}")

@router.post("/portfolio-alerts/{alert_id}/mark-read")
async def mark_alert_as_read(
    alert_id: str,
    current_user = Depends(get_current_user)
):
    """Mark a news alert as read"""
    try:
        if alert_id not in mock_portfolio_alerts:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = mock_portfolio_alerts[alert_id]
        
        if alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        alert.is_read = True
        
        return {"message": "Alert marked as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking alert as read: {str(e)}")

@router.get("/sentiment-heatmap", response_model=NewsHeatmap)
async def get_sentiment_heatmap(
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(get_current_user)
):
    """Get sentiment heatmap for market overview"""
    try:
        # Get sector sentiment
        sector_sentiments = await get_sector_sentiment(hours, current_user)
        
        # Get company impacts
        company_impacts = await get_company_news_impact(None, hours, current_user)
        
        # Calculate overall market mood
        overall_sentiment = sum(s.sentiment_score for s in sector_sentiments) / len(sector_sentiments)
        
        if overall_sentiment > 0.3:
            market_mood = "optimistic"
        elif overall_sentiment < -0.3:
            market_mood = "pessimistic"
        else:
            market_mood = "cautious"
        
        # Calculate volatility indicator
        sentiment_variance = sum((s.sentiment_score - overall_sentiment) ** 2 for s in sector_sentiments) / len(sector_sentiments)
        
        if sentiment_variance > 0.5:
            volatility_indicator = "high"
        elif sentiment_variance > 0.2:
            volatility_indicator = "medium"
        else:
            volatility_indicator = "low"
        
        heatmap = NewsHeatmap(
            sectors=sector_sentiments,
            companies=company_impacts,
            market_mood=market_mood,
            volatility_indicator=volatility_indicator,
            generated_at=datetime.now()
        )
        
        return heatmap
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sentiment heatmap: {str(e)}")

@router.get("/news-sources", response_model=List[NewsSource])
async def get_news_sources():
    """Get list of monitored news sources"""
    try:
        sources = [
            NewsSource(
                name="Medias24",
                url="https://www.medias24.com",
                language=NewsLanguage.FRENCH,
                reliability_score=Decimal('85'),
                last_updated=datetime.now()
            ),
            NewsSource(
                name="Le Matin",
                url="https://www.lematin.ma",
                language=NewsLanguage.FRENCH,
                reliability_score=Decimal('80'),
                last_updated=datetime.now()
            ),
            NewsSource(
                name="L'Economiste",
                url="https://www.leconomiste.com",
                language=NewsLanguage.FRENCH,
                reliability_score=Decimal('90'),
                last_updated=datetime.now()
            ),
            NewsSource(
                name="Hespress",
                url="https://www.hespress.com",
                language=NewsLanguage.ARABIC,
                reliability_score=Decimal('75'),
                last_updated=datetime.now()
            ),
            NewsSource(
                name="Morocco World News",
                url="https://www.moroccoworldnews.com",
                language=NewsLanguage.ENGLISH,
                reliability_score=Decimal('80'),
                last_updated=datetime.now()
            )
        ]
        
        return sources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news sources: {str(e)}")

# Helper functions
async def generate_mock_news_articles():
    """Generate mock news articles for demonstration"""
    articles = [
        NewsArticle(
            id=str(uuid.uuid4()),
            title="Attijariwafa Bank Reports Strong Q4 Results",
            title_ar="التجاري وفا بنك يحقق نتائج قوية في الربع الرابع",
            content="Attijariwafa Bank announced strong quarterly results driven by digital transformation initiatives...",
            content_ar="أعلن التجاري وفا بنك عن نتائج ربع سنوية قوية مدفوعة بمبادرات التحول الرقمي...",
            source="Medias24",
            source_url="https://www.medias24.com",
            language=NewsLanguage.FRENCH,
            published_at=datetime.now() - timedelta(hours=2),
            companies_mentioned=["ATW"],
            sectors_mentioned=["banking"],
            sentiment_score=Decimal('0.7'),
            sentiment_label=SentimentScore.POSITIVE,
            impact_score=Decimal('85'),
            is_breaking=False
        ),
        NewsArticle(
            id=str(uuid.uuid4()),
            title="OCP Group Announces New Phosphate Mine Development",
            title_ar="مجموعة المكتب الشريف للفوسفاط تعلن عن تطوير منجم فوسفات جديد",
            content="OCP Group unveiled plans for a new phosphate mining operation in the Gantour region...",
            content_ar="كشفت مجموعة المكتب الشريف للفوسفاط عن خطط لعملية تعدين فوسفات جديدة في منطقة كنتور...",
            source="L'Economiste",
            source_url="https://www.leconomiste.com",
            language=NewsLanguage.FRENCH,
            published_at=datetime.now() - timedelta(hours=4),
            companies_mentioned=["OCP"],
            sectors_mentioned=["mining"],
            sentiment_score=Decimal('0.8'),
            sentiment_label=SentimentScore.POSITIVE,
            impact_score=Decimal('90'),
            is_breaking=True
        ),
        NewsArticle(
            id=str(uuid.uuid4()),
            title="Maroc Telecom Faces Regulatory Challenges",
            title_ar="اتصالات المغرب تواجه تحديات تنظيمية",
            content="Maroc Telecom is facing new regulatory challenges regarding pricing policies...",
            content_ar="تواجه اتصالات المغرب تحديات تنظيمية جديدة فيما يتعلق بسياسات التسعير...",
            source="Le Matin",
            source_url="https://www.lematin.ma",
            language=NewsLanguage.FRENCH,
            published_at=datetime.now() - timedelta(hours=6),
            companies_mentioned=["IAM"],
            sectors_mentioned=["telecommunications"],
            sentiment_score=Decimal('-0.4'),
            sentiment_label=SentimentScore.NEGATIVE,
            impact_score=Decimal('70'),
            is_breaking=False
        )
    ]
    
    for article in articles:
        mock_news_articles[article.id] = article

async def generate_ai_summary(article: NewsArticle) -> NewsSummary:
    """Generate AI-powered news summary"""
    # Mock AI summarization
    summary_en = f"Summary of {article.title}: Key developments affecting {', '.join(article.companies_mentioned)}. Market impact expected to be {'positive' if article.sentiment_score > 0 else 'negative'}."
    summary_ar = f"ملخص {article.title_ar or article.title}: التطورات الرئيسية التي تؤثر على {', '.join(article.companies_mentioned)}. من المتوقع أن يكون التأثير على السوق {'إيجابي' if article.sentiment_score > 0 else 'سلبي'}."
    
    key_points = [
        f"Affects {', '.join(article.companies_mentioned)}",
        f"Sentiment: {article.sentiment_label.value}",
        f"Impact score: {article.impact_score}/100"
    ]
    
    return NewsSummary(
        article_id=article.id,
        summary_en=summary_en,
        summary_ar=summary_ar,
        key_points=key_points,
        market_impact=f"{'Positive' if article.sentiment_score > 0 else 'Negative'} impact expected",
        affected_companies=article.companies_mentioned,
        confidence_score=Decimal('85'),
        generated_at=datetime.now()
    )

async def perform_sentiment_analysis(article: NewsArticle) -> SentimentAnalysis:
    """Perform sentiment analysis on news article"""
    # Mock sentiment analysis
    emotions = {
        "joy": Decimal('0.3') if article.sentiment_score > 0 else Decimal('0.1'),
        "anger": Decimal('0.1') if article.sentiment_score > 0 else Decimal('0.4'),
        "fear": Decimal('0.2') if article.sentiment_score < 0 else Decimal('0.1'),
        "surprise": Decimal('0.3'),
        "sadness": Decimal('0.1') if article.sentiment_score > 0 else Decimal('0.3')
    }
    
    market_implications = []
    if article.sentiment_score > 0.5:
        market_implications.append("Likely positive price movement")
        market_implications.append("Increased investor confidence")
    elif article.sentiment_score < -0.5:
        market_implications.append("Potential negative price impact")
        market_implications.append("Increased market volatility")
    else:
        market_implications.append("Neutral market impact expected")
    
    return SentimentAnalysis(
        article_id=article.id,
        overall_sentiment=article.sentiment_label,
        sentiment_score=article.sentiment_score,
        confidence=Decimal('85'),
        emotions=emotions,
        market_implications=market_implications,
        analyzed_at=datetime.now()
    )

async def calculate_sector_sentiment(sector: str, hours: int) -> Decimal:
    """Calculate sentiment score for a sector"""
    # Mock calculation
    import random
    return Decimal(str(random.uniform(-0.8, 0.8)))

async def count_sector_articles(sector: str, hours: int) -> int:
    """Count articles for a sector"""
    # Mock count
    import random
    return random.randint(1, 20)

def get_sentiment_label(score: Decimal) -> SentimentScore:
    """Convert sentiment score to label"""
    if score > 0.6:
        return SentimentScore.VERY_POSITIVE
    elif score > 0.2:
        return SentimentScore.POSITIVE
    elif score > -0.2:
        return SentimentScore.NEUTRAL
    elif score > -0.6:
        return SentimentScore.NEGATIVE
    else:
        return SentimentScore.VERY_NEGATIVE

def get_volume_indicator(sector: str) -> str:
    """Get volume indicator for sector"""
    # Mock volume indicator
    import random
    return random.choice(["low", "medium", "high"])

async def calculate_company_news_impact(ticker: str, hours: int) -> CompanyNewsImpact:
    """Calculate news impact for a company"""
    company_names = {
        "ATW": "Attijariwafa Bank",
        "IAM": "Maroc Telecom",
        "BCP": "Banque Centrale Populaire",
        "OCP": "Office Chérifien des Phosphates",
        "BMCE": "BMCE Bank",
        "CMT": "Ciments du Maroc",
        "LAFA": "Lafarge Ciments",
        "CIH": "CIH Bank",
        "MNG": "Managem",
        "TMA": "Taqa Morocco"
    }
    
    # Mock impact calculation
    import random
    impact_score = Decimal(str(random.uniform(20, 95)))
    sentiment_score = Decimal(str(random.uniform(-0.8, 0.8)))
    
    # Get relevant news articles
    relevant_articles = [
        article for article in mock_news_articles.values()
        if ticker in article.companies_mentioned
    ][:3]  # Latest 3 articles
    
    impact_type = "positive" if sentiment_score > 0.2 else "negative" if sentiment_score < -0.2 else "neutral"
    urgency = "high" if impact_score > 80 else "medium" if impact_score > 50 else "low"
    
    return CompanyNewsImpact(
        ticker=ticker,
        company_name=company_names.get(ticker, ticker),
        impact_score=impact_score,
        sentiment_score=sentiment_score,
        news_count=len(relevant_articles),
        latest_news=relevant_articles,
        impact_type=impact_type,
        urgency=urgency
    )

async def update_portfolio_alerts(article: NewsArticle, user_id: str):
    """Update portfolio alerts based on news article"""
    # Mock alert generation
    for ticker in article.companies_mentioned:
        if article.impact_score > 75:  # High impact threshold
            alert_id = str(uuid.uuid4())
            alert = PortfolioNewsAlert(
                id=alert_id,
                user_id=user_id,
                portfolio_id="default",  # Mock portfolio ID
                article_id=article.id,
                ticker=ticker,
                impact_score=article.impact_score,
                alert_type="high_impact" if article.impact_score > 80 else "sentiment_change",
                message=f"High impact news for {ticker}: {article.title}",
                sent_at=datetime.now(),
                is_read=False
            )
            mock_portfolio_alerts[alert_id] = alert