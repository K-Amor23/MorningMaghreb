from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ============================================
# ENUMS
# ============================================

class ReportType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    FINANCIAL_STATEMENT = "financial_statement"
    EARNINGS = "earnings"
    UNKNOWN = "unknown"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class IndicatorType(str, Enum):
    RSI = "rsi"
    MACD = "macd"
    MOVING_AVERAGE = "moving_average"
    VOLUME = "volume"
    SENTIMENT = "sentiment"
    EARNINGS = "earnings"

class SizeCategory(str, Enum):
    MICRO_CAP = "Micro Cap"
    SMALL_CAP = "Small Cap"
    MID_CAP = "Mid Cap"
    LARGE_CAP = "Large Cap"

class DataQualityLevel(str, Enum):
    PARTIAL = "Partial"
    COMPLETE = "Complete"

# ============================================
# BASE MODELS
# ============================================

class CompanyBase(BaseModel):
    ticker: str = Field(..., description="Company ticker symbol", max_length=10)
    name: str = Field(..., description="Company name", max_length=255)
    sector: Optional[str] = Field(None, description="Company sector", max_length=100)
    industry: Optional[str] = Field(None, description="Company industry", max_length=100)
    market_cap_billion: Optional[Decimal] = Field(None, description="Market capitalization in billions")
    price: Optional[Decimal] = Field(None, description="Current stock price")
    change_1d_percent: Optional[Decimal] = Field(None, description="1-day price change percentage")
    change_ytd_percent: Optional[Decimal] = Field(None, description="Year-to-date price change percentage")
    size_category: Optional[SizeCategory] = Field(None, description="Company size category")
    sector_group: Optional[str] = Field(None, description="Sector group", max_length=100)
    exchange: str = Field(default="Casablanca Stock Exchange (BVC)", description="Stock exchange")
    country: str = Field(default="Morocco", description="Country")
    company_url: Optional[str] = Field(None, description="Company website URL")
    ir_url: Optional[str] = Field(None, description="Investor relations URL")
    is_active: bool = Field(default=True, description="Whether company is active")

    @validator('ticker')
    def validate_ticker(cls, v):
        if not v.isalpha() or not v.isupper():
            raise ValueError('Ticker must be uppercase letters only')
        return v

class PriceData(BaseModel):
    date: date = Field(..., description="Trading date")
    open: Optional[Decimal] = Field(None, description="Opening price")
    high: Optional[Decimal] = Field(None, description="High price")
    low: Optional[Decimal] = Field(None, description="Low price")
    close: Optional[Decimal] = Field(None, description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    adjusted_close: Optional[Decimal] = Field(None, description="Adjusted closing price")

    @validator('high')
    def validate_high_low(cls, v, values):
        if v is not None and 'low' in values and values['low'] is not None:
            if v < values['low']:
                raise ValueError('High price cannot be less than low price')
        return v

class ReportData(BaseModel):
    title: str = Field(..., description="Report title", max_length=500)
    report_type: ReportType = Field(..., description="Type of report")
    report_date: Optional[str] = Field(None, description="Report date string")
    report_year: Optional[str] = Field(None, description="Report year")
    report_quarter: Optional[str] = Field(None, description="Report quarter")
    url: str = Field(..., description="Report URL")
    filename: Optional[str] = Field(None, description="Report filename")
    scraped_at: datetime = Field(..., description="When report was scraped")

    @validator('report_year')
    def validate_year(cls, v):
        if v is not None and not v.isdigit() or len(v) != 4:
            raise ValueError('Year must be a 4-digit number')
        return v

class NewsData(BaseModel):
    headline: str = Field(..., description="News headline")
    source: Optional[str] = Field(None, description="News source", max_length=255)
    published_at: Optional[datetime] = Field(None, description="Publication date")
    sentiment: Optional[SentimentType] = Field(None, description="Sentiment analysis")
    sentiment_score: Optional[Decimal] = Field(None, description="Sentiment score (-1 to 1)")
    url: Optional[str] = Field(None, description="News URL")
    content_preview: Optional[str] = Field(None, description="Content preview")
    scraped_at: datetime = Field(..., description="When news was scraped")

    @validator('sentiment_score')
    def validate_sentiment_score(cls, v):
        if v is not None and (v < -1 or v > 1):
            raise ValueError('Sentiment score must be between -1 and 1')
        return v

class AnalyticsSignal(BaseModel):
    signal_date: date = Field(..., description="Signal date")
    signal_type: SignalType = Field(..., description="Signal type")
    indicator: IndicatorType = Field(..., description="Technical indicator")
    value: Optional[Decimal] = Field(None, description="Indicator value")
    threshold: Optional[Decimal] = Field(None, description="Signal threshold")
    confidence: Optional[Decimal] = Field(None, description="Signal confidence (0-1)")
    description: Optional[str] = Field(None, description="Signal description")

    @validator('confidence')
    def validate_confidence(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Confidence must be between 0 and 1')
        return v

# ============================================
# RESPONSE MODELS
# ============================================

class CompanySummary(BaseModel):
    company: CompanyBase
    current_price: Optional[Decimal] = Field(None, description="Current stock price")
    price_change: Optional[Decimal] = Field(None, description="Price change")
    price_change_percent: Optional[Decimal] = Field(None, description="Price change percentage")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    volume: Optional[int] = Field(None, description="Trading volume")
    pe_ratio: Optional[Decimal] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[Decimal] = Field(None, description="Dividend yield")
    roe: Optional[Decimal] = Field(None, description="Return on equity")
    last_updated: datetime = Field(..., description="Last data update")
    data_quality: DataQualityLevel = Field(..., description="Data quality level")

class TradingData(BaseModel):
    ticker: str = Field(..., description="Company ticker")
    prices: List[PriceData] = Field(..., description="Historical price data")
    current_price: Optional[Decimal] = Field(None, description="Current price")
    price_change: Optional[Decimal] = Field(None, description="Price change")
    price_change_percent: Optional[Decimal] = Field(None, description="Price change percentage")
    volume: Optional[int] = Field(None, description="Current volume")
    signals: List[AnalyticsSignal] = Field(default_factory=list, description="Technical signals")
    last_updated: datetime = Field(..., description="Last data update")
    data_quality: DataQualityLevel = Field(..., description="Data quality level")

class ReportsData(BaseModel):
    ticker: str = Field(..., description="Company ticker")
    reports: List[ReportData] = Field(..., description="Financial reports")
    total_reports: int = Field(..., description="Total number of reports")
    latest_report: Optional[ReportData] = Field(None, description="Most recent report")
    report_types: Dict[str, int] = Field(default_factory=dict, description="Count by report type")
    last_updated: datetime = Field(..., description="Last data update")
    data_quality: DataQualityLevel = Field(..., description="Data quality level")

class NewsData(BaseModel):
    ticker: str = Field(..., description="Company ticker")
    news: List[NewsData] = Field(..., description="News articles")
    total_news: int = Field(..., description="Total number of news articles")
    sentiment_summary: Dict[str, int] = Field(default_factory=dict, description="Sentiment distribution")
    average_sentiment: Optional[Decimal] = Field(None, description="Average sentiment score")
    last_updated: datetime = Field(..., description="Last data update")
    data_quality: DataQualityLevel = Field(..., description="Data quality level")

# ============================================
# ERROR MODELS
# ============================================

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

class ValidationError(BaseModel):
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value")

# ============================================
# QUERY PARAMETER MODELS
# ============================================

class TradingQueryParams(BaseModel):
    days: Optional[int] = Field(default=90, ge=1, le=365, description="Number of days of data")
    include_signals: bool = Field(default=True, description="Include technical signals")

class ReportsQueryParams(BaseModel):
    report_type: Optional[ReportType] = Field(None, description="Filter by report type")
    year: Optional[str] = Field(None, description="Filter by year")
    limit: Optional[int] = Field(default=50, ge=1, le=100, description="Number of reports to return")

class NewsQueryParams(BaseModel):
    sentiment: Optional[SentimentType] = Field(None, description="Filter by sentiment")
    days: Optional[int] = Field(default=30, ge=1, le=365, description="Number of days of news")
    limit: Optional[int] = Field(default=50, ge=1, le=100, description="Number of news articles to return") 