from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Import models
from models.company import (
    CompanySummary, TradingData, ReportsData, NewsData,
    CompanyBase, PriceData, ReportData, NewsData as NewsDataModel,
    AnalyticsSignal, TradingQueryParams, ReportsQueryParams, NewsQueryParams,
    ErrorResponse, DataQualityLevel, ReportType, SentimentType
)

# Import database utilities
from database.connection import get_db_session
from services.analytics_service import AnalyticsService
from services.data_integration_service import DataIntegrationService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# DEPENDENCIES
# ============================================

async def get_analytics_service() -> AnalyticsService:
    """Dependency to get analytics service"""
    return AnalyticsService()

async def get_data_integration_service() -> DataIntegrationService:
    """Dependency to get data integration service"""
    return DataIntegrationService()

# ============================================
# UTILITY FUNCTIONS
# ============================================

def assess_data_quality(company_data: Dict[str, Any], prices_data: List[Dict], 
                       reports_data: List[Dict], news_data: List[Dict]) -> DataQualityLevel:
    """Assess data quality based on completeness and freshness"""
    score = 0
    total_checks = 0
    
    # Company data quality
    if company_data:
        total_checks += 1
        if all(company_data.get(field) for field in ['ticker', 'name', 'price', 'market_cap_billion']):
            score += 1
    
    # Price data quality
    if prices_data:
        total_checks += 1
        recent_prices = [p for p in prices_data if p.get('date') and 
                        datetime.strptime(p['date'], '%Y-%m-%d').date() >= date.today() - timedelta(days=7)]
        if len(recent_prices) >= 5:  # At least 5 recent price points
            score += 1
    
    # Reports data quality
    if reports_data:
        total_checks += 1
        recent_reports = [r for r in reports_data if r.get('scraped_at') and 
                         datetime.fromisoformat(r['scraped_at'].replace('Z', '+00:00')) >= 
                         datetime.utcnow() - timedelta(days=90)]
        if len(recent_reports) >= 2:  # At least 2 recent reports
            score += 1
    
    # News data quality
    if news_data:
        total_checks += 1
        recent_news = [n for n in news_data if n.get('published_at') and 
                      datetime.fromisoformat(n['published_at'].replace('Z', '+00:00')) >= 
                      datetime.utcnow() - timedelta(days=30)]
        if len(recent_news) >= 5:  # At least 5 recent news articles
            score += 1
    
    quality_ratio = score / total_checks if total_checks > 0 else 0
    return DataQualityLevel.COMPLETE if quality_ratio >= 0.75 else DataQualityLevel.PARTIAL

async def get_company_data(db: AsyncSession, ticker: str) -> Dict[str, Any]:
    """Get company basic data from database"""
    try:
        query = text("""
            SELECT id, ticker, name, sector, industry, market_cap_billion, price,
                   change_1d_percent, change_ytd_percent, size_category, sector_group,
                   exchange, country, company_url, ir_url, is_active, updated_at
            FROM companies 
            WHERE ticker = :ticker AND is_active = true
        """)
        result = await db.execute(query, {"ticker": ticker.upper()})
        company = result.fetchone()
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")
        
        return dict(company._mapping)
    except Exception as e:
        logger.error(f"Error fetching company data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_price_data(db: AsyncSession, ticker: str, days: int = 90) -> List[Dict[str, Any]]:
    """Get historical price data from database"""
    try:
        query = text("""
            SELECT date, open, high, low, close, volume, adjusted_close
            FROM company_prices 
            WHERE ticker = :ticker 
            AND date >= CURRENT_DATE - INTERVAL ':days days'
            ORDER BY date DESC
        """)
        result = await db.execute(query, {"ticker": ticker.upper(), "days": days})
        prices = result.fetchall()
        
        return [dict(price._mapping) for price in prices]
    except Exception as e:
        logger.error(f"Error fetching price data for {ticker}: {e}")
        return []

async def get_reports_data(db: AsyncSession, ticker: str, report_type: Optional[str] = None, 
                          year: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get financial reports data from database"""
    try:
        where_clause = "WHERE ticker = :ticker"
        params = {"ticker": ticker.upper(), "limit": limit}
        
        if report_type:
            where_clause += " AND report_type = :report_type"
            params["report_type"] = report_type
        
        if year:
            where_clause += " AND report_year = :year"
            params["year"] = year
        
        query = text(f"""
            SELECT title, report_type, report_date, report_year, report_quarter,
                   url, filename, scraped_at
            FROM company_reports 
            {where_clause}
            ORDER BY scraped_at DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, params)
        reports = result.fetchall()
        
        return [dict(report._mapping) for report in reports]
    except Exception as e:
        logger.error(f"Error fetching reports data for {ticker}: {e}")
        return []

async def get_news_data(db: AsyncSession, ticker: str, sentiment: Optional[str] = None,
                       days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
    """Get news data from database"""
    try:
        where_clause = "WHERE ticker = :ticker"
        params = {"ticker": ticker.upper(), "limit": limit}
        
        if sentiment:
            where_clause += " AND sentiment = :sentiment"
            params["sentiment"] = sentiment
        
        where_clause += " AND published_at >= CURRENT_DATE - INTERVAL ':days days'"
        params["days"] = days
        
        query = text(f"""
            SELECT headline, source, published_at, sentiment, sentiment_score,
                   url, content_preview, scraped_at
            FROM company_news 
            {where_clause}
            ORDER BY published_at DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, params)
        news = result.fetchall()
        
        return [dict(article._mapping) for article in news]
    except Exception as e:
        logger.error(f"Error fetching news data for {ticker}: {e}")
        return []

# ============================================
# API ENDPOINTS
# ============================================

@router.get(
    "/{ticker}/summary",
    response_model=CompanySummary,
    responses={
        200: {"description": "Company summary data retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Company not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get company summary",
    description="Retrieve comprehensive summary data for a specific company including basic info, current price, and key metrics."
)
async def get_company_summary(
    ticker: str = Path(..., description="Company ticker symbol", example="BCP"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get comprehensive company summary data"""
    try:
        # Validate ticker format
        if not ticker.isalpha() or not ticker.isupper():
            raise HTTPException(status_code=400, detail="Ticker must be uppercase letters only")
        
        # Get company data
        company_data = await get_company_data(db, ticker)
        
        # Get recent price data for current metrics
        prices_data = await get_price_data(db, ticker, days=7)
        
        # Get recent reports for data quality assessment
        reports_data = await get_reports_data(db, ticker, limit=5)
        
        # Get recent news for data quality assessment
        news_data = await get_news_data(db, ticker, days=30, limit=5)
        
        # Assess data quality
        data_quality = assess_data_quality(company_data, prices_data, reports_data, news_data)
        
        # Get current price from most recent price data
        current_price = None
        price_change = None
        price_change_percent = None
        volume = None
        
        if prices_data:
            latest_price = prices_data[0]  # Most recent
            current_price = latest_price.get('close')
            
            if len(prices_data) >= 2:
                previous_price = prices_data[1]  # Previous day
                if current_price and previous_price.get('close'):
                    price_change = current_price - previous_price['close']
                    price_change_percent = (price_change / previous_price['close']) * 100
                    volume = latest_price.get('volume')
        
        # Build response
        company_base = CompanyBase(
            ticker=company_data['ticker'],
            name=company_data['name'],
            sector=company_data['sector'],
            industry=company_data['industry'],
            market_cap_billion=company_data['market_cap_billion'],
            price=company_data['price'],
            change_1d_percent=company_data['change_1d_percent'],
            change_ytd_percent=company_data['change_ytd_percent'],
            size_category=company_data['size_category'],
            sector_group=company_data['sector_group'],
            exchange=company_data['exchange'],
            country=company_data['country'],
            company_url=company_data['company_url'],
            ir_url=company_data['ir_url'],
            is_active=company_data['is_active']
        )
        
        return CompanySummary(
            company=company_base,
            current_price=current_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            market_cap=company_data['market_cap_billion'],
            volume=volume,
            pe_ratio=None,  # TODO: Calculate from financial data
            dividend_yield=None,  # TODO: Calculate from dividend data
            roe=None,  # TODO: Calculate from financial data
            last_updated=company_data['updated_at'],
            data_quality=data_quality
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_company_summary for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/{ticker}/trading",
    response_model=TradingData,
    responses={
        200: {"description": "Trading data retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Company not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get company trading data",
    description="Retrieve historical price data and technical signals for a specific company."
)
async def get_company_trading(
    ticker: str = Path(..., description="Company ticker symbol", example="BCP"),
    days: int = Query(default=90, ge=1, le=365, description="Number of days of data"),
    include_signals: bool = Query(default=True, description="Include technical signals"),
    db: AsyncSession = Depends(get_db_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get company trading data and technical signals"""
    try:
        # Validate ticker format
        if not ticker.isalpha() or not ticker.isupper():
            raise HTTPException(status_code=400, detail="Ticker must be uppercase letters only")
        
        # Verify company exists
        company_data = await get_company_data(db, ticker)
        
        # Get price data
        prices_data = await get_price_data(db, ticker, days)
        
        if not prices_data:
            raise HTTPException(status_code=404, detail=f"No price data found for {ticker}")
        
        # Convert to Pydantic models
        prices = []
        for price_dict in prices_data:
            prices.append(PriceData(
                date=price_dict['date'],
                open=price_dict['open'],
                high=price_dict['high'],
                low=price_dict['low'],
                close=price_dict['close'],
                volume=price_dict['volume'],
                adjusted_close=price_dict['adjusted_close']
            ))
        
        # Get current metrics
        current_price = prices[0].close if prices else None
        price_change = None
        price_change_percent = None
        volume = prices[0].volume if prices else None
        
        if len(prices) >= 2:
            price_change = current_price - prices[1].close if current_price and prices[1].close else None
            price_change_percent = (price_change / prices[1].close * 100) if price_change and prices[1].close else None
        
        # Get technical signals if requested
        signals = []
        if include_signals and len(prices) >= 14:  # Need enough data for technical analysis
            try:
                # Convert prices to format expected by analytics service
                price_series = [(p.date, p.close) for p in prices if p.close]
                signals_data = await analytics_service.generate_signals(ticker, price_series)
                
                for signal_dict in signals_data:
                    signals.append(AnalyticsSignal(
                        signal_date=signal_dict['signal_date'],
                        signal_type=signal_dict['signal_type'],
                        indicator=signal_dict['indicator'],
                        value=signal_dict.get('value'),
                        threshold=signal_dict.get('threshold'),
                        confidence=signal_dict.get('confidence'),
                        description=signal_dict.get('description')
                    ))
            except Exception as e:
                logger.warning(f"Could not generate signals for {ticker}: {e}")
        
        # Assess data quality
        data_quality = assess_data_quality(company_data, prices_data, [], [])
        
        return TradingData(
            ticker=ticker.upper(),
            prices=prices,
            current_price=current_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            volume=volume,
            signals=signals,
            last_updated=company_data['updated_at'],
            data_quality=data_quality
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_company_trading for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/{ticker}/reports",
    response_model=ReportsData,
    responses={
        200: {"description": "Reports data retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Company not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get company reports",
    description="Retrieve financial reports and documents for a specific company."
)
async def get_company_reports(
    ticker: str = Path(..., description="Company ticker symbol", example="BCP"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    year: Optional[str] = Query(None, description="Filter by year"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of reports to return"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get company financial reports"""
    try:
        # Validate ticker format
        if not ticker.isalpha() or not ticker.isupper():
            raise HTTPException(status_code=400, detail="Ticker must be uppercase letters only")
        
        # Verify company exists
        company_data = await get_company_data(db, ticker)
        
        # Get reports data
        reports_data = await get_reports_data(db, ticker, report_type, year, limit)
        
        # Convert to Pydantic models
        reports = []
        for report_dict in reports_data:
            reports.append(ReportData(
                title=report_dict['title'],
                report_type=report_dict['report_type'],
                report_date=report_dict['report_date'],
                report_year=report_dict['report_year'],
                report_quarter=report_dict['report_quarter'],
                url=report_dict['url'],
                filename=report_dict['filename'],
                scraped_at=report_dict['scraped_at']
            ))
        
        # Calculate summary statistics
        total_reports = len(reports)
        latest_report = reports[0] if reports else None
        
        # Count by report type
        report_types = {}
        for report in reports:
            report_type_str = report.report_type.value
            report_types[report_type_str] = report_types.get(report_type_str, 0) + 1
        
        # Assess data quality
        data_quality = assess_data_quality(company_data, [], reports_data, [])
        
        return ReportsData(
            ticker=ticker.upper(),
            reports=reports,
            total_reports=total_reports,
            latest_report=latest_report,
            report_types=report_types,
            last_updated=company_data['updated_at'],
            data_quality=data_quality
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_company_reports for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/{ticker}/news",
    response_model=NewsData,
    responses={
        200: {"description": "News data retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Company not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get company news",
    description="Retrieve news articles and sentiment analysis for a specific company."
)
async def get_company_news(
    ticker: str = Path(..., description="Company ticker symbol", example="BCP"),
    sentiment: Optional[SentimentType] = Query(None, description="Filter by sentiment"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days of news"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of news articles to return"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get company news and sentiment"""
    try:
        # Validate ticker format
        if not ticker.isalpha() or not ticker.isupper():
            raise HTTPException(status_code=400, detail="Ticker must be uppercase letters only")
        
        # Verify company exists
        company_data = await get_company_data(db, ticker)
        
        # Get news data
        news_data = await get_news_data(db, ticker, sentiment, days, limit)
        
        # Convert to Pydantic models
        news_articles = []
        for news_dict in news_data:
            news_articles.append(NewsDataModel(
                headline=news_dict['headline'],
                source=news_dict['source'],
                published_at=news_dict['published_at'],
                sentiment=news_dict['sentiment'],
                sentiment_score=news_dict['sentiment_score'],
                url=news_dict['url'],
                content_preview=news_dict['content_preview'],
                scraped_at=news_dict['scraped_at']
            ))
        
        # Calculate summary statistics
        total_news = len(news_articles)
        
        # Sentiment distribution
        sentiment_summary = {}
        sentiment_scores = []
        
        for article in news_articles:
            if article.sentiment:
                sentiment_summary[article.sentiment.value] = sentiment_summary.get(article.sentiment.value, 0) + 1
            if article.sentiment_score is not None:
                sentiment_scores.append(article.sentiment_score)
        
        # Average sentiment
        average_sentiment = None
        if sentiment_scores:
            average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Assess data quality
        data_quality = assess_data_quality(company_data, [], [], news_data)
        
        return NewsData(
            ticker=ticker.upper(),
            news=news_articles,
            total_news=total_news,
            sentiment_summary=sentiment_summary,
            average_sentiment=average_sentiment,
            last_updated=company_data['updated_at'],
            data_quality=data_quality
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_company_news for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================
# ERROR HANDLERS
# ============================================

@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.utcnow()
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    ) 