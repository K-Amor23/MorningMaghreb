from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging
from pydantic import BaseModel

from models.financials import FinancialSummary
from models.economic_data import EconomicIndicatorType, EconomicDataPoint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])

# Request/Response Models
class CompanyComparisonRequest(BaseModel):
    companies: List[str]
    metrics: List[str] = ["revenue", "net_income", "roe", "pe_ratio", "debt_equity"]
    year: Optional[int] = None
    quarter: Optional[int] = None

class CompanyComparisonResponse(BaseModel):
    companies: List[str]
    metrics: List[str]
    data: Dict[str, Dict[str, Any]]
    comparison_chart_data: Dict[str, Any]

class EarningsCalendarRequest(BaseModel):
    start_date: date
    end_date: date
    companies: Optional[List[str]] = None

class EarningsEvent(BaseModel):
    company: str
    ticker: str
    earnings_date: date
    estimate: Optional[float]
    actual: Optional[float]
    surprise: Optional[float]
    sector: str

class DividendEvent(BaseModel):
    company: str
    ticker: str
    ex_date: date
    payment_date: date
    amount: float
    dividend_yield: float
    payout_ratio: float
    frequency: str

class CustomScreenRequest(BaseModel):
    name: str
    filters: Dict[str, Any]
    user_id: str

class CustomScreenResponse(BaseModel):
    id: str
    name: str
    filters: Dict[str, Any]
    results: List[Dict[str, Any]]
    created_at: datetime
    last_run: datetime

# Company Comparison Tool
@router.post("/compare", response_model=CompanyComparisonResponse)
async def compare_companies(
    request: CompanyComparisonRequest,
    user: dict = Depends(lambda: {"id": "mock_user"})  # Mock auth
):
    """Compare 2-3 Moroccan companies side-by-side"""
    try:
        if len(request.companies) < 2 or len(request.companies) > 3:
            raise HTTPException(status_code=400, detail="Must compare 2-3 companies")
        
        # Mock data for demonstration
        comparison_data = {}
        chart_data = {
            "labels": request.companies,
            "datasets": []
        }
        
        for company in request.companies:
            # Mock financial data
            company_data = {
                "revenue": 40000000000 + hash(company) % 20000000000,
                "net_income": 8000000000 + hash(company) % 4000000000,
                "roe": 15.0 + hash(company) % 10,
                "pe_ratio": 12.0 + hash(company) % 8,
                "debt_equity": 0.8 + (hash(company) % 10) / 10,
                "market_cap": 100000000000 + hash(company) % 50000000000,
                "dividend_yield": 3.5 + (hash(company) % 5) / 10
            }
            comparison_data[company] = company_data
        
        # Prepare chart data
        for metric in request.metrics:
            if metric in ["revenue", "net_income", "market_cap"]:
                values = [comparison_data[company][metric] for company in request.companies]
                chart_data["datasets"].append({
                    "label": metric.replace("_", " ").title(),
                    "data": values,
                    "backgroundColor": f"rgba({hash(metric) % 255}, {hash(metric) % 255}, 255, 0.6)"
                })
        
        return CompanyComparisonResponse(
            companies=request.companies,
            metrics=request.metrics,
            data=comparison_data,
            comparison_chart_data=chart_data
        )
        
    except Exception as e:
        logger.error(f"Error comparing companies: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare companies")

# Earnings Calendar
@router.post("/earnings-calendar", response_model=List[EarningsEvent])
async def get_earnings_calendar(
    request: EarningsCalendarRequest,
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """Get upcoming earnings releases for Moroccan companies"""
    try:
        # Mock earnings data
        mock_earnings = [
            EarningsEvent(
                company="Attijariwafa Bank",
                ticker="ATW",
                earnings_date=date(2024, 11, 15),
                estimate=4.2,
                actual=None,
                surprise=None,
                sector="Banking"
            ),
            EarningsEvent(
                company="Maroc Telecom",
                ticker="IAM",
                earnings_date=date(2024, 11, 20),
                estimate=1.8,
                actual=None,
                surprise=None,
                sector="Telecommunications"
            ),
            EarningsEvent(
                company="Banque Centrale Populaire",
                ticker="BCP",
                earnings_date=date(2024, 11, 25),
                estimate=2.8,
                actual=None,
                surprise=None,
                sector="Banking"
            ),
            EarningsEvent(
                company="BMCE Bank",
                ticker="BMCE",
                earnings_date=date(2024, 12, 5),
                estimate=1.5,
                actual=None,
                surprise=None,
                sector="Banking"
            )
        ]
        
        # Filter by date range
        filtered_earnings = [
            earning for earning in mock_earnings
            if request.start_date <= earning.earnings_date <= request.end_date
        ]
        
        # Filter by companies if specified
        if request.companies:
            filtered_earnings = [
                earning for earning in filtered_earnings
                if earning.ticker in request.companies
            ]
        
        return filtered_earnings
        
    except Exception as e:
        logger.error(f"Error getting earnings calendar: {e}")
        raise HTTPException(status_code=500, detail="Failed to get earnings calendar")

# Dividend Tracker
@router.get("/dividends", response_model=List[DividendEvent])
async def get_dividend_events(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    min_yield: Optional[float] = Query(None, description="Minimum dividend yield"),
    max_yield: Optional[float] = Query(None, description="Maximum dividend yield"),
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """Get dividend events with filtering options"""
    try:
        # Mock dividend data
        mock_dividends = [
            DividendEvent(
                company="Attijariwafa Bank",
                ticker="ATW",
                ex_date=date(2024, 12, 15),
                payment_date=date(2024, 12, 20),
                amount=15.0,
                dividend_yield=4.1,
                payout_ratio=45.2,
                frequency="Semi-annual"
            ),
            DividendEvent(
                company="Maroc Telecom",
                ticker="IAM",
                ex_date=date(2024, 12, 10),
                payment_date=date(2024, 12, 15),
                amount=3.5,
                dividend_yield=4.6,
                payout_ratio=52.1,
                frequency="Semi-annual"
            ),
            DividendEvent(
                company="Banque Centrale Populaire",
                ticker="BCP",
                ex_date=date(2024, 12, 20),
                payment_date=date(2024, 12, 25),
                amount=8.5,
                dividend_yield=3.8,
                payout_ratio=38.5,
                frequency="Semi-annual"
            ),
            DividendEvent(
                company="Wafa Assurance",
                ticker="WAA",
                ex_date=date(2024, 11, 30),
                payment_date=date(2024, 12, 5),
                amount=2.1,
                dividend_yield=5.2,
                payout_ratio=65.3,
                frequency="Annual"
            )
        ]
        
        # Apply filters
        filtered_dividends = mock_dividends
        
        if start_date:
            filtered_dividends = [d for d in filtered_dividends if d.ex_date >= start_date]
        if end_date:
            filtered_dividends = [d for d in filtered_dividends if d.ex_date <= end_date]
        if min_yield:
            filtered_dividends = [d for d in filtered_dividends if d.dividend_yield >= min_yield]
        if max_yield:
            filtered_dividends = [d for d in filtered_dividends if d.dividend_yield <= max_yield]
        
        return filtered_dividends
        
    except Exception as e:
        logger.error(f"Error getting dividend events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dividend events")

# Economic Indicator Tracker
@router.get("/economic-dashboard", response_model=Dict[str, Any])
async def get_economic_dashboard(
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """Get comprehensive economic dashboard with trends and AI summaries"""
    try:
        # Mock economic data with trends
        economic_data = {
            "key_policy_rate": {
                "current_value": 3.0,
                "previous_value": 3.0,
                "change": 0.0,
                "trend": "stable",
                "chart_data": [
                    {"date": "2024-01", "value": 3.0},
                    {"date": "2024-02", "value": 3.0},
                    {"date": "2024-03", "value": 3.0},
                    {"date": "2024-04", "value": 3.0},
                    {"date": "2024-05", "value": 3.0},
                    {"date": "2024-06", "value": 3.0}
                ],
                "ai_summary": "Policy rate remains stable at 3.0% as BAM maintains accommodative stance to support economic recovery."
            },
            "inflation_cpi": {
                "current_value": 2.8,
                "previous_value": 2.5,
                "change": 0.3,
                "trend": "increasing",
                "chart_data": [
                    {"date": "2024-01", "value": 2.1},
                    {"date": "2024-02", "value": 2.2},
                    {"date": "2024-03", "value": 2.3},
                    {"date": "2024-04", "value": 2.4},
                    {"date": "2024-05", "value": 2.5},
                    {"date": "2024-06", "value": 2.8}
                ],
                "ai_summary": "Inflation rose to 2.8% in June, driven by food and energy prices. Still within BAM's target range."
            },
            "foreign_exchange_reserves": {
                "current_value": 3500000000000,
                "previous_value": 3450000000000,
                "change": 1.45,
                "trend": "increasing",
                "chart_data": [
                    {"date": "2024-01", "value": 3300000000000},
                    {"date": "2024-02", "value": 3350000000000},
                    {"date": "2024-03", "value": 3400000000000},
                    {"date": "2024-04", "value": 3420000000000},
                    {"date": "2024-05", "value": 3450000000000},
                    {"date": "2024-06", "value": 3500000000000}
                ],
                "ai_summary": "FX reserves increased to 350B MAD, providing strong external buffer and supporting currency stability."
            }
        }
        
        return {
            "indicators": economic_data,
            "last_updated": datetime.now().isoformat(),
            "overall_trend": "stable",
            "market_sentiment": "positive"
        }
        
    except Exception as e:
        logger.error(f"Error getting economic dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get economic dashboard")

# Custom Screens
@router.post("/screens", response_model=CustomScreenResponse)
async def create_custom_screen(
    request: CustomScreenRequest,
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """Create a new custom screen with filters"""
    try:
        # Mock screen creation
        screen_id = f"screen_{hash(request.name) % 10000}"
        
        # Mock results based on filters
        mock_companies = [
            {"ticker": "ATW", "name": "Attijariwafa Bank", "pe_ratio": 11.3, "dividend_yield": 4.1},
            {"ticker": "BCP", "name": "Banque Centrale Populaire", "pe_ratio": 14.7, "dividend_yield": 3.8},
            {"ticker": "WAA", "name": "Wafa Assurance", "pe_ratio": 9.2, "dividend_yield": 5.2},
            {"ticker": "CMA", "name": "Ciments du Maroc", "pe_ratio": 13.1, "dividend_yield": 3.5}
        ]
        
        # Apply filters (simplified)
        filtered_results = mock_companies
        if "pe_ratio_max" in request.filters:
            filtered_results = [c for c in filtered_results if c["pe_ratio"] <= request.filters["pe_ratio_max"]]
        if "dividend_yield_min" in request.filters:
            filtered_results = [c for c in filtered_results if c["dividend_yield"] >= request.filters["dividend_yield_min"]]
        
        return CustomScreenResponse(
            id=screen_id,
            name=request.name,
            filters=request.filters,
            results=filtered_results,
            created_at=datetime.now(),
            last_run=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error creating custom screen: {e}")
        raise HTTPException(status_code=500, detail="Failed to create custom screen")

@router.get("/screens/{screen_id}", response_model=CustomScreenResponse)
async def get_custom_screen(
    screen_id: str,
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """Get a specific custom screen"""
    try:
        # Mock screen retrieval
        return CustomScreenResponse(
            id=screen_id,
            name="Value Stocks Screen",
            filters={"pe_ratio_max": 15, "dividend_yield_min": 3.0},
            results=[
                {"ticker": "ATW", "name": "Attijariwafa Bank", "pe_ratio": 11.3, "dividend_yield": 4.1},
                {"ticker": "WAA", "name": "Wafa Assurance", "pe_ratio": 9.2, "dividend_yield": 5.2}
            ],
            created_at=datetime.now(),
            last_run=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting custom screen: {e}")
        raise HTTPException(status_code=500, detail="Failed to get custom screen")

@router.get("/screens", response_model=List[Dict[str, Any]])
async def list_custom_screens(
    user: dict = Depends(lambda: {"id": "mock_user"})
):
    """List all custom screens for a user"""
    try:
        # Mock screens list
        return [
            {
                "id": "screen_1",
                "name": "Value Stocks Screen",
                "filters": {"pe_ratio_max": 15, "dividend_yield_min": 3.0},
                "created_at": datetime.now().isoformat(),
                "last_run": datetime.now().isoformat()
            },
            {
                "id": "screen_2", 
                "name": "High Dividend Screen",
                "filters": {"dividend_yield_min": 4.0},
                "created_at": datetime.now().isoformat(),
                "last_run": datetime.now().isoformat()
            }
        ]
        
    except Exception as e:
        logger.error(f"Error listing custom screens: {e}")
        raise HTTPException(status_code=500, detail="Failed to list custom screens") 