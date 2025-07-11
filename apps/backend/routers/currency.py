from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging

from ..models.currency import (
    BAMRate, RemittanceRate, RateAlert, RateAnalysis, 
    CurrencyComparison, RateAlertCreate, RateAlertResponse
)
from ..etl.currency_scraper import CurrencyScraper
from ..lib.database import get_db
from ..lib.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/currency", tags=["currency"])

@router.get("/compare/{currency_pair}", response_model=CurrencyComparison)
async def compare_rates(
    currency_pair: str = "USD/MAD",
    amount: Decimal = Query(1000, description="Transfer amount in USD"),
    db: Session = Depends(get_db)
):
    """Compare remittance rates against BAM official rate"""
    try:
        scraper = CurrencyScraper()
        
        # Fetch BAM rate
        bam_data = await scraper.fetch_bam_rate(currency_pair)
        if not bam_data:
            raise HTTPException(status_code=500, detail="Could not fetch BAM rate")
        
        # Fetch all remittance rates
        remittance_rates_data = await scraper.fetch_all_remittance_rates(currency_pair, amount)
        
        # Find best rate
        best_rate_data = scraper.find_best_rate(remittance_rates_data, bam_data['rate'])
        
        # Calculate 30-day percentile (mock for now)
        percentile_30d = 75  # Mock: today's rate is better than 75% of past 30 days
        
        # Generate AI recommendation
        recommendation = generate_ai_recommendation(
            bam_data['rate'], 
            best_rate_data.get('effective_rate', 0),
            best_rate_data.get('service_name', ''),
            percentile_30d
        )
        
        # Determine if it's a good time
        is_good_time = percentile_30d >= 70  # Good if better than 70% of past 30 days
        
        comparison = CurrencyComparison(
            currency_pair=currency_pair,
            bam_rate=bam_data['rate'],
            services=[RemittanceRate(**rate) for rate in remittance_rates_data],
            best_service=best_rate_data.get('service_name', ''),
            best_rate=best_rate_data.get('effective_rate', 0),
            best_spread=best_rate_data.get('spread_percentage', 0),
            recommendation=recommendation,
            is_good_time=is_good_time,
            percentile_30d=percentile_30d
        )
        
        await scraper.close()
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing rates: {e}")
        raise HTTPException(status_code=500, detail="Error comparing rates")

@router.get("/bam-rate/{currency_pair}", response_model=BAMRate)
async def get_bam_rate(currency_pair: str = "USD/MAD"):
    """Get official BAM exchange rate"""
    try:
        scraper = CurrencyScraper()
        bam_data = await scraper.fetch_bam_rate(currency_pair)
        await scraper.close()
        
        if not bam_data:
            raise HTTPException(status_code=404, detail="BAM rate not available")
        
        return BAMRate(**bam_data)
        
    except Exception as e:
        logger.error(f"Error fetching BAM rate: {e}")
        raise HTTPException(status_code=500, detail="Error fetching BAM rate")

@router.get("/remittance-rates/{currency_pair}", response_model=List[RemittanceRate])
async def get_remittance_rates(
    currency_pair: str = "USD/MAD",
    amount: Decimal = Query(1000, description="Transfer amount")
):
    """Get rates from all remittance services"""
    try:
        scraper = CurrencyScraper()
        rates_data = await scraper.fetch_all_remittance_rates(currency_pair, amount)
        await scraper.close()
        
        return [RemittanceRate(**rate) for rate in rates_data]
        
    except Exception as e:
        logger.error(f"Error fetching remittance rates: {e}")
        raise HTTPException(status_code=500, detail="Error fetching remittance rates")

@router.post("/alerts", response_model=RateAlertResponse)
async def create_rate_alert(
    alert: RateAlertCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new rate alert"""
    try:
        # In production, save to database
        # For now, return mock response
        alert_response = RateAlertResponse(
            id="123e4567-e89b-12d3-a456-426614174000",  # Mock UUID
            currency_pair=alert.currency_pair,
            target_rate=alert.target_rate,
            alert_type=alert.alert_type,
            is_active=True,
            created_at=datetime.now()
        )
        
        return alert_response
        
    except Exception as e:
        logger.error(f"Error creating rate alert: {e}")
        raise HTTPException(status_code=500, detail="Error creating rate alert")

@router.get("/alerts", response_model=List[RateAlertResponse])
async def get_user_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's rate alerts"""
    try:
        # In production, fetch from database
        # For now, return mock data
        mock_alerts = [
            RateAlertResponse(
                id="123e4567-e89b-12d3-a456-426614174000",
                currency_pair="USD/MAD",
                target_rate=Decimal("10.00"),
                alert_type="above",
                is_active=True,
                created_at=datetime.now()
            )
        ]
        
        return mock_alerts
        
    except Exception as e:
        logger.error(f"Error fetching user alerts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching alerts")

@router.delete("/alerts/{alert_id}")
async def delete_rate_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a rate alert"""
    try:
        # In production, delete from database
        return {"message": "Alert deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting rate alert: {e}")
        raise HTTPException(status_code=500, detail="Error deleting alert")

@router.get("/history/{currency_pair}", response_model=List[RateAnalysis])
async def get_rate_history(
    currency_pair: str = "USD/MAD",
    days: int = Query(30, description="Number of days of history")
):
    """Get historical rate analysis"""
    try:
        # In production, fetch from database
        # For now, return mock data
        mock_history = []
        for i in range(days):
            date_offset = date.today() - timedelta(days=i)
            mock_history.append(RateAnalysis(
                currency_pair=currency_pair,
                analysis_date=date_offset,
                bam_rate=Decimal("10.25") + Decimal(str(i * 0.01)),
                best_service="Remitly",
                best_rate=Decimal("10.15") + Decimal(str(i * 0.01)),
                best_spread=Decimal("0.98"),
                avg_spread_30d=Decimal("1.2"),
                percentile_30d=75,
                ai_advice="Today's rate is favorable for transfers"
            ))
        
        return mock_history
        
    except Exception as e:
        logger.error(f"Error fetching rate history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching rate history")

def generate_ai_recommendation(
    bam_rate: Decimal, 
    best_rate: Decimal, 
    best_service: str, 
    percentile: int
) -> str:
    """Generate AI-powered recommendation"""
    spread = ((bam_rate - best_rate) / bam_rate) * 100
    
    if percentile >= 80:
        timing_advice = "Excellent timing! Today's rate is better than 80% of the past 30 days."
    elif percentile >= 60:
        timing_advice = "Good timing. Today's rate is above average."
    else:
        timing_advice = "Consider waiting. Today's rate is below average."
    
    if spread <= 1.0:
        spread_advice = f"Great deal! {best_service} offers only {spread:.2f}% below BAM rate."
    elif spread <= 2.0:
        spread_advice = f"Reasonable spread. {best_service} is {spread:.2f}% below BAM rate."
    else:
        spread_advice = f"High spread. {best_service} is {spread:.2f}% below BAM rate. Consider alternatives."
    
    return f"{timing_advice} {spread_advice}" 