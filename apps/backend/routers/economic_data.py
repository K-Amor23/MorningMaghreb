from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging

from models.economic_data import (
    EconomicIndicatorType, EconomicDataResponse, EconomicDataSummary,
    EconomicDataBulkResponse, EconomicDataETLJob
)
from etl.fetch_economic_data import EconomicDataFetcher
from storage.local_fs import LocalFileStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/economic-data", tags=["Economic Data"])

# Dependency to get the economic data fetcher
def get_economic_data_fetcher():
    storage = LocalFileStorage()
    return EconomicDataFetcher(storage)

@router.get("/", response_model=Dict[str, Any])
async def get_economic_data_summary(
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Get summary of available economic data"""
    try:
        summary = await fetcher.get_data_summary()
        return {
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting economic data summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get economic data summary")

@router.get("/indicators", response_model=List[str])
async def get_available_indicators():
    """Get list of available economic indicators"""
    return [indicator.value for indicator in EconomicIndicatorType]

@router.get("/{indicator}", response_model=EconomicDataResponse)
async def get_economic_data(
    indicator: EconomicIndicatorType,
    start_date: Optional[date] = Query(None, description="Start date for data range"),
    end_date: Optional[date] = Query(None, description="End date for data range"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of data points to return"),
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Get economic data for a specific indicator"""
    try:
        # For now, return mock data structure
        # In production, this would query the database
        mock_data_points = []
        
        # Generate some mock data points
        base_date = date(2023, 1, 1)
        for i in range(min(limit, 12)):
            data_date = date(base_date.year, base_date.month + i, 1)
            if start_date and data_date < start_date:
                continue
            if end_date and data_date > end_date:
                continue
                
            mock_data_points.append({
                "date": data_date,
                "value": 100.0 + i * 2.5,  # Mock increasing trend
                "unit": "MAD" if indicator in [EconomicIndicatorType.FOREIGN_EXCHANGE_RESERVES, 
                                             EconomicIndicatorType.MONEY_SUPPLY,
                                             EconomicIndicatorType.BALANCE_OF_PAYMENTS,
                                             EconomicIndicatorType.CREDIT_TO_ECONOMY] else "percent",
                "indicator": indicator,
                "source": "BAM",
                "confidence": 0.95
            })
        
        # Create summary
        if mock_data_points:
            latest_point = mock_data_points[-1]
            summary = EconomicDataSummary(
                indicator=indicator,
                latest_value=latest_point["value"],
                latest_date=latest_point["date"],
                unit=latest_point["unit"],
                frequency="monthly",
                source="BAM",
                last_updated=datetime.now(),
                trend="up",
                change_percentage=2.5
            )
        else:
            summary = EconomicDataSummary(
                indicator=indicator,
                latest_value=None,
                latest_date=None,
                unit="MAD",
                frequency="monthly",
                source="BAM",
                last_updated=datetime.now()
            )
        
        return EconomicDataResponse(
            indicator=indicator,
            data_points=mock_data_points,
            summary=summary,
            metadata={
                "total_points": len(mock_data_points),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "source": "BAM"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting economic data for {indicator}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get economic data for {indicator}")

@router.get("/{indicator}/latest", response_model=EconomicDataSummary)
async def get_latest_economic_data(
    indicator: EconomicIndicatorType,
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Get the latest data point for a specific indicator"""
    try:
        latest_data = await fetcher.get_latest_data(indicator.value)
        
        if latest_data:
            return EconomicDataSummary(
                indicator=indicator,
                latest_value=latest_data.get("value"),
                latest_date=latest_data.get("latest_date"),
                unit=latest_data.get("unit", "MAD"),
                frequency="monthly",
                source="BAM",
                last_updated=datetime.now()
            )
        else:
            return EconomicDataSummary(
                indicator=indicator,
                latest_value=None,
                latest_date=None,
                unit="MAD",
                frequency="monthly",
                source="BAM",
                last_updated=datetime.now()
            )
            
    except Exception as e:
        logger.error(f"Error getting latest economic data for {indicator}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest economic data for {indicator}")

@router.post("/fetch", response_model=Dict[str, Any])
async def fetch_economic_data(
    indicators: Optional[List[EconomicIndicatorType]] = Query(None, description="Specific indicators to fetch"),
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Trigger fetching of economic data from BAM"""
    try:
        indicator_names = [ind.value for ind in indicators] if indicators else None
        
        logger.info(f"Starting economic data fetch for indicators: {indicator_names}")
        
        results = await fetcher.fetch_all_economic_data(indicator_names)
        
        return {
            "status": "success",
            "message": "Economic data fetch completed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching economic data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch economic data")

@router.get("/compare/{indicator1}/{indicator2}", response_model=Dict[str, Any])
async def compare_indicators(
    indicator1: EconomicIndicatorType,
    indicator2: EconomicIndicatorType,
    start_date: Optional[date] = Query(None, description="Start date for comparison"),
    end_date: Optional[date] = Query(None, description="End date for comparison"),
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Compare two economic indicators over time"""
    try:
        # This would fetch and compare data for both indicators
        # For now, return mock comparison data
        
        comparison_data = {
            "indicator1": {
                "name": indicator1,
                "data": [],
                "summary": {
                    "avg_value": 105.0,
                    "trend": "up",
                    "volatility": 2.1
                }
            },
            "indicator2": {
                "name": indicator2,
                "data": [],
                "summary": {
                    "avg_value": 3.2,
                    "trend": "stable",
                    "volatility": 0.5
                }
            },
            "correlation": 0.15,
            "comparison_period": {
                "start": start_date.isoformat() if start_date else "2023-01-01",
                "end": end_date.isoformat() if end_date else "2023-12-31"
            }
        }
        
        return {
            "status": "success",
            "data": comparison_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing indicators {indicator1} and {indicator2}: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare indicators")

@router.get("/trends/{indicator}", response_model=Dict[str, Any])
async def get_indicator_trends(
    indicator: EconomicIndicatorType,
    period: str = Query("12m", description="Analysis period (3m, 6m, 12m, 24m)"),
    fetcher: EconomicDataFetcher = Depends(get_economic_data_fetcher)
):
    """Get trend analysis for a specific indicator"""
    try:
        # Mock trend analysis
        trends = {
            "indicator": indicator,
            "period": period,
            "trend": "upward",
            "trend_strength": 0.75,
            "seasonality": "moderate",
            "forecast": {
                "next_month": 107.5,
                "next_quarter": 110.2,
                "confidence_interval": [105.0, 112.0]
            },
            "key_insights": [
                "Steady upward trend over the past 12 months",
                "Seasonal patterns observed in Q2 and Q4",
                "Above-average growth compared to historical data"
            ]
        }
        
        return {
            "status": "success",
            "data": trends,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trends for {indicator}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get indicator trends")

@router.get("/dashboard/overview", response_model=Dict[str, Any])
async def get_economic_dashboard():
    """Get overview dashboard with key economic indicators"""
    try:
        dashboard_data = {
            "last_updated": datetime.now().isoformat(),
            "key_indicators": {
                "key_policy_rate": {
                    "current_value": 3.0,
                    "unit": "percent",
                    "trend": "stable",
                    "change": 0.0,
                    "last_update": "2024-01-15"
                },
                "inflation_cpi": {
                    "current_value": 2.8,
                    "unit": "percent",
                    "trend": "down",
                    "change": -0.2,
                    "last_update": "2024-01-10"
                },
                "foreign_exchange_reserves": {
                    "current_value": 350000,
                    "unit": "MAD millions",
                    "trend": "up",
                    "change": 2.5,
                    "last_update": "2024-01-12"
                }
            },
            "market_sentiment": "positive",
            "economic_outlook": "stable",
            "next_important_dates": [
                {"date": "2024-02-15", "event": "BAM Policy Rate Decision"},
                {"date": "2024-02-20", "event": "CPI Data Release"},
                {"date": "2024-03-01", "event": "Foreign Exchange Reserves Update"}
            ]
        }
        
        return {
            "status": "success",
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error getting economic dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get economic dashboard") 