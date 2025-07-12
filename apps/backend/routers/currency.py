from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging

from models.currency import (
    BAMRate, RemittanceRate, RateAlert, RateAnalysis, 
    CurrencyComparison, RateAlertCreate, RateAlertResponse
)
from etl.currency_scraper import CurrencyScraper
from database.database import get_db
from utils.auth import get_current_user

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

@router.get("/trends/{currency_pair}")
async def get_rate_trends(
    currency_pair: str = "USD/MAD",
    days: int = Query(7, description="Number of days of trend data")
):
    """Get rate trend data for charting"""
    try:
        # Mock trend data - in production, fetch from database
        trends = []
        base_date = date.today()
        base_bam_rate = Decimal("10.25")
        base_best_rate = Decimal("10.15")
        
        for i in range(days):
            trend_date = base_date - timedelta(days=i)
            # Add some realistic variation
            variation = (i % 3 - 1) * Decimal("0.02")  # Small variations
            
            trends.append({
                "date": trend_date.isoformat(),
                "bam_rate": float(base_bam_rate + variation),
                "best_rate": float(base_best_rate + variation),
                "avg_rate": float(base_bam_rate + variation * Decimal("0.5"))
            })
        
        return {"trends": trends}
        
    except Exception as e:
        logger.error(f"Error fetching rate trends: {e}")
        raise HTTPException(status_code=500, detail="Error fetching rate trends")

@router.get("/insights/{currency_pair}")
async def get_crowdsource_insights(
    currency_pair: str = "USD/MAD",
    limit: int = Query(10, description="Number of insights to return")
):
    """Get crowdsourced insights and tips"""
    try:
        # Mock crowdsource data - in production, fetch from database
        insights = [
            {
                "id": "1",
                "user_type": "Frequent User",
                "message": "Remitly usually has the best rates on Tuesdays and Wednesdays. Avoid weekends!",
                "rating": 4.8,
                "timestamp": "2 hours ago",
                "likes": 23,
                "helpful_count": 15
            },
            {
                "id": "2", 
                "user_type": "Expat",
                "message": "I always check Bank Al-Maghrib rate first, then compare with Wise. Usually saves me 1-2%",
                "rating": 4.6,
                "timestamp": "5 hours ago",
                "likes": 18,
                "helpful_count": 12
            },
            {
                "id": "3",
                "user_type": "Business Owner", 
                "message": "Western Union has good rates for large amounts (>$5000). Smaller amounts, go with Remitly.",
                "rating": 4.4,
                "timestamp": "1 day ago",
                "likes": 15,
                "helpful_count": 8
            },
            {
                "id": "4",
                "user_type": "Student",
                "message": "CIH Bank has the best rates for students with student accounts. Check their special programs!",
                "rating": 4.7,
                "timestamp": "2 days ago", 
                "likes": 12,
                "helpful_count": 6
            }
        ]
        
        return {"insights": insights[:limit]}
        
    except Exception as e:
        logger.error(f"Error fetching crowdsource insights: {e}")
        raise HTTPException(status_code=500, detail="Error fetching insights")

@router.get("/forecast/{currency_pair}")
async def get_ai_forecast(
    currency_pair: str = "USD/MAD",
    days: int = Query(3, description="Number of days to forecast")
):
    """Get AI-powered rate forecast"""
    try:
        # Mock AI forecast - in production, use ML model
        forecast = {
            "currency_pair": currency_pair,
            "forecast_date": date.today().isoformat(),
            "predictions": [],
            "confidence": 0.78,
            "model_version": "v1.0",
            "factors": [
                "BAM policy rate stability",
                "USD strength index", 
                "Moroccan trade balance",
                "Global market sentiment"
            ]
        }
        
        base_rate = Decimal("10.25")
        for i in range(1, days + 1):
            # Simple trend prediction
            trend = Decimal("0.01") if i % 2 == 0 else Decimal("-0.005")
            predicted_rate = base_rate + trend * i
            
            forecast["predictions"].append({
                "date": (date.today() + timedelta(days=i)).isoformat(),
                "predicted_rate": float(predicted_rate),
                "confidence_interval": [float(predicted_rate - Decimal("0.02")), float(predicted_rate + Decimal("0.02"))],
                "trend": "up" if trend > 0 else "down"
            })
        
        return forecast
        
    except Exception as e:
        logger.error(f"Error generating AI forecast: {e}")
        raise HTTPException(status_code=500, detail="Error generating forecast")

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