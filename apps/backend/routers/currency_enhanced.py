from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging
import asyncio

from models.currency import (
    BAMRate, RemittanceRate, RateAlert, RateAnalysis, 
    CurrencyComparison, RateAlertCreate, RateAlertResponse
)
from etl.currency_scraper import CurrencyScraper
from database.database import get_db
from utils.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/currency-enhanced", tags=["currency-enhanced"])

# Enhanced Models
class CurrencyBasketItem(BaseModel):
    currency_code: str
    currency_name: str
    rate: Decimal
    change_24h: Decimal
    change_percentage: Decimal
    strength_index: Decimal
    trend: str  # 'up', 'down', 'stable'
    volume: Optional[Decimal] = None

class CurrencyBasket(BaseModel):
    base_currency: str
    base_currency_name: str
    currencies: List[CurrencyBasketItem]
    last_updated: datetime

class CurrencyStrengthIndex(BaseModel):
    currency_code: str
    strength_score: Decimal  # 0-100
    trend: str
    factors: List[str]

class CrossCurrencyAnalysis(BaseModel):
    base_currency: str
    target_currency: str
    direct_rate: Decimal
    cross_rate_via_usd: Decimal
    arbitrage_opportunity: bool
    potential_profit: Decimal

class RegionalCurrencyComparison(BaseModel):
    base_currency: str
    regional_currencies: List[CurrencyBasketItem]
    major_currencies: List[CurrencyBasketItem]
    best_performing: str
    worst_performing: str

@router.get("/basket", response_model=CurrencyBasket)
async def get_currency_basket(
    base_currency: str = Query("MAD", description="Base currency for comparison"),
    include_regional: bool = Query(True, description="Include regional currencies"),
    include_major: bool = Query(True, description="Include major world currencies"),
    db: Session = Depends(get_db)
):
    """Get multi-currency basket against MAD"""
    try:
        scraper = CurrencyScraper()
        
        # Define currency lists
        major_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        regional_currencies = ["SAR", "AED", "EGP", "TND", "DZD", "XOF"]  # West African CFA
        
        # Currency names mapping
        currency_names = {
            "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", 
            "JPY": "Japanese Yen", "CHF": "Swiss Franc", "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar", "SAR": "Saudi Riyal", "AED": "UAE Dirham",
            "EGP": "Egyptian Pound", "TND": "Tunisian Dinar", "DZD": "Algerian Dinar",
            "XOF": "West African CFA Franc", "MAD": "Moroccan Dirham"
        }
        
        currencies_to_fetch = []
        if include_major:
            currencies_to_fetch.extend(major_currencies)
        if include_regional:
            currencies_to_fetch.extend(regional_currencies)
        
        # Remove base currency from list
        currencies_to_fetch = [c for c in currencies_to_fetch if c != base_currency]
        
        # Fetch rates concurrently
        basket_items = []
        
        for currency in currencies_to_fetch:
            try:
                currency_pair = f"{currency}/{base_currency}"
                
                # Get current rate
                rate_data = await scraper.fetch_bam_rate(currency_pair)
                if not rate_data:
                    # Use mock data for demonstration
                    rate_data = generate_mock_rate_data(currency, base_currency)
                
                # Calculate 24h change (mock for now)
                change_24h = Decimal(str(rate_data.get('change_24h', 0)))
                current_rate = Decimal(str(rate_data.get('rate', 0)))
                
                if current_rate > 0:
                    change_percentage = (change_24h / current_rate) * 100
                else:
                    change_percentage = Decimal('0')
                
                # Calculate strength index
                strength_index = await calculate_currency_strength_index(currency, base_currency)
                
                # Determine trend
                trend = "up" if change_24h > 0 else "down" if change_24h < 0 else "stable"
                
                basket_item = CurrencyBasketItem(
                    currency_code=currency,
                    currency_name=currency_names.get(currency, currency),
                    rate=current_rate,
                    change_24h=change_24h,
                    change_percentage=change_percentage,
                    strength_index=strength_index,
                    trend=trend,
                    volume=Decimal('1000000')  # Mock volume
                )
                
                basket_items.append(basket_item)
                
            except Exception as e:
                logger.warning(f"Failed to fetch rate for {currency}: {e}")
                continue
        
        # Sort by strength index (descending)
        basket_items.sort(key=lambda x: x.strength_index, reverse=True)
        
        basket = CurrencyBasket(
            base_currency=base_currency,
            base_currency_name=currency_names.get(base_currency, base_currency),
            currencies=basket_items,
            last_updated=datetime.now()
        )
        
        await scraper.close()
        return basket
        
    except Exception as e:
        logger.error(f"Error fetching currency basket: {e}")
        raise HTTPException(status_code=500, detail="Error fetching currency basket")

@router.get("/strength-index/{currency_code}", response_model=CurrencyStrengthIndex)
async def get_currency_strength_index(
    currency_code: str,
    vs_currency: str = Query("MAD", description="Base currency for comparison"),
    db: Session = Depends(get_db)
):
    """Get currency strength index"""
    try:
        strength_score = await calculate_currency_strength_index(currency_code, vs_currency)
        
        # Determine trend based on recent performance
        trend = "up" if strength_score > 60 else "down" if strength_score < 40 else "stable"
        
        # Mock factors that influence strength
        factors = get_currency_strength_factors(currency_code)
        
        return CurrencyStrengthIndex(
            currency_code=currency_code,
            strength_score=strength_score,
            trend=trend,
            factors=factors
        )
        
    except Exception as e:
        logger.error(f"Error calculating currency strength index: {e}")
        raise HTTPException(status_code=500, detail="Error calculating strength index")

@router.get("/cross-analysis/{currency1}/{currency2}", response_model=CrossCurrencyAnalysis)
async def get_cross_currency_analysis(
    currency1: str,
    currency2: str,
    db: Session = Depends(get_db)
):
    """Analyze cross-currency rates and arbitrage opportunities"""
    try:
        scraper = CurrencyScraper()
        
        # Get direct rate
        direct_pair = f"{currency1}/{currency2}"
        direct_rate_data = await scraper.fetch_bam_rate(direct_pair)
        direct_rate = Decimal(str(direct_rate_data.get('rate', 0))) if direct_rate_data else Decimal('0')
        
        # Get cross rate via USD
        usd_rate1_data = await scraper.fetch_bam_rate(f"{currency1}/USD")
        usd_rate2_data = await scraper.fetch_bam_rate(f"{currency2}/USD")
        
        if usd_rate1_data and usd_rate2_data:
            usd_rate1 = Decimal(str(usd_rate1_data.get('rate', 0)))
            usd_rate2 = Decimal(str(usd_rate2_data.get('rate', 0)))
            
            if usd_rate2 > 0:
                cross_rate_via_usd = usd_rate1 / usd_rate2
            else:
                cross_rate_via_usd = Decimal('0')
        else:
            cross_rate_via_usd = Decimal('0')
        
        # Check for arbitrage opportunity
        arbitrage_opportunity = False
        potential_profit = Decimal('0')
        
        if direct_rate > 0 and cross_rate_via_usd > 0:
            rate_difference = abs(direct_rate - cross_rate_via_usd)
            arbitrage_threshold = Decimal('0.01')  # 1% threshold
            
            if rate_difference > arbitrage_threshold:
                arbitrage_opportunity = True
                potential_profit = (rate_difference / direct_rate) * 100
        
        analysis = CrossCurrencyAnalysis(
            base_currency=currency1,
            target_currency=currency2,
            direct_rate=direct_rate,
            cross_rate_via_usd=cross_rate_via_usd,
            arbitrage_opportunity=arbitrage_opportunity,
            potential_profit=potential_profit
        )
        
        await scraper.close()
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing cross-currency rates: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing cross-currency rates")

@router.get("/regional-comparison", response_model=RegionalCurrencyComparison)
async def get_regional_currency_comparison(
    base_currency: str = Query("MAD", description="Base currency for comparison"),
    db: Session = Depends(get_db)
):
    """Get regional currency comparison for MENA and African markets"""
    try:
        scraper = CurrencyScraper()
        
        # Regional currencies (MENA + Africa)
        regional_currencies = ["SAR", "AED", "EGP", "TND", "DZD", "XOF", "ZAR", "NGN"]
        major_currencies = ["USD", "EUR", "GBP", "JPY"]
        
        currency_names = {
            "SAR": "Saudi Riyal", "AED": "UAE Dirham", "EGP": "Egyptian Pound",
            "TND": "Tunisian Dinar", "DZD": "Algerian Dinar", "XOF": "West African CFA Franc",
            "ZAR": "South African Rand", "NGN": "Nigerian Naira",
            "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound", "JPY": "Japanese Yen"
        }
        
        async def fetch_currency_data(currencies: List[str]) -> List[CurrencyBasketItem]:
            items = []
            for currency in currencies:
                if currency == base_currency:
                    continue
                    
                try:
                    currency_pair = f"{currency}/{base_currency}"
                    rate_data = await scraper.fetch_bam_rate(currency_pair)
                    
                    if not rate_data:
                        rate_data = generate_mock_rate_data(currency, base_currency)
                    
                    current_rate = Decimal(str(rate_data.get('rate', 0)))
                    change_24h = Decimal(str(rate_data.get('change_24h', 0)))
                    change_percentage = (change_24h / current_rate) * 100 if current_rate > 0 else Decimal('0')
                    
                    strength_index = await calculate_currency_strength_index(currency, base_currency)
                    trend = "up" if change_24h > 0 else "down" if change_24h < 0 else "stable"
                    
                    items.append(CurrencyBasketItem(
                        currency_code=currency,
                        currency_name=currency_names.get(currency, currency),
                        rate=current_rate,
                        change_24h=change_24h,
                        change_percentage=change_percentage,
                        strength_index=strength_index,
                        trend=trend
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {currency}: {e}")
                    continue
            
            return items
        
        # Fetch data concurrently
        regional_data = await fetch_currency_data(regional_currencies)
        major_data = await fetch_currency_data(major_currencies)
        
        # Find best and worst performers
        all_currencies = regional_data + major_data
        if all_currencies:
            best_performing = max(all_currencies, key=lambda x: x.change_percentage).currency_code
            worst_performing = min(all_currencies, key=lambda x: x.change_percentage).currency_code
        else:
            best_performing = worst_performing = "N/A"
        
        comparison = RegionalCurrencyComparison(
            base_currency=base_currency,
            regional_currencies=regional_data,
            major_currencies=major_data,
            best_performing=best_performing,
            worst_performing=worst_performing
        )
        
        await scraper.close()
        return comparison
        
    except Exception as e:
        logger.error(f"Error fetching regional currency comparison: {e}")
        raise HTTPException(status_code=500, detail="Error fetching regional comparison")

@router.get("/heatmap", response_model=Dict[str, Any])
async def get_currency_heatmap(
    base_currency: str = Query("MAD", description="Base currency for comparison"),
    db: Session = Depends(get_db)
):
    """Get currency performance heatmap data"""
    try:
        # Get currency basket data
        basket = await get_currency_basket(base_currency, include_regional=True, include_major=True, db=db)
        
        # Organize data for heatmap
        heatmap_data = {
            "base_currency": base_currency,
            "timestamp": datetime.now().isoformat(),
            "major_currencies": [],
            "regional_currencies": [],
            "performance_summary": {
                "strongest": "",
                "weakest": "",
                "most_volatile": "",
                "least_volatile": ""
            }
        }
        
        # Categorize currencies
        major_codes = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
        
        for currency in basket.currencies:
            currency_data = {
                "code": currency.currency_code,
                "name": currency.currency_name,
                "rate": float(currency.rate),
                "change_24h": float(currency.change_24h),
                "change_percentage": float(currency.change_percentage),
                "strength_index": float(currency.strength_index),
                "trend": currency.trend
            }
            
            if currency.currency_code in major_codes:
                heatmap_data["major_currencies"].append(currency_data)
            else:
                heatmap_data["regional_currencies"].append(currency_data)
        
        # Calculate performance summary
        all_currencies = basket.currencies
        if all_currencies:
            strongest = max(all_currencies, key=lambda x: x.strength_index)
            weakest = min(all_currencies, key=lambda x: x.strength_index)
            most_volatile = max(all_currencies, key=lambda x: abs(x.change_percentage))
            least_volatile = min(all_currencies, key=lambda x: abs(x.change_percentage))
            
            heatmap_data["performance_summary"] = {
                "strongest": strongest.currency_code,
                "weakest": weakest.currency_code,
                "most_volatile": most_volatile.currency_code,
                "least_volatile": least_volatile.currency_code
            }
        
        return heatmap_data
        
    except Exception as e:
        logger.error(f"Error generating currency heatmap: {e}")
        raise HTTPException(status_code=500, detail="Error generating currency heatmap")

async def calculate_currency_strength_index(currency_code: str, base_currency: str) -> Decimal:
    """Calculate currency strength index (0-100)"""
    try:
        # Mock calculation - in production, this would use multiple factors
        # Factors: inflation rate, interest rates, economic growth, political stability, etc.
        
        strength_factors = {
            "USD": 85, "EUR": 75, "GBP": 70, "JPY": 65, "CHF": 80,
            "CAD": 72, "AUD": 68, "SAR": 60, "AED": 58, "EGP": 35,
            "TND": 45, "DZD": 40, "XOF": 42, "ZAR": 50, "NGN": 30,
            "MAD": 55
        }
        
        base_strength = strength_factors.get(currency_code, 50)
        
        # Add some randomness for demonstration
        import random
        variation = random.uniform(-5, 5)
        
        strength_score = max(0, min(100, base_strength + variation))
        
        return Decimal(str(strength_score))
        
    except Exception as e:
        logger.error(f"Error calculating currency strength: {e}")
        return Decimal('50')  # Default neutral strength

def get_currency_strength_factors(currency_code: str) -> List[str]:
    """Get factors that influence currency strength"""
    factors_map = {
        "USD": ["Federal Reserve policy", "US economic growth", "Global demand", "Trade balance"],
        "EUR": ["ECB monetary policy", "Eurozone stability", "Inflation rates", "Political unity"],
        "GBP": ["Bank of England policy", "Brexit impact", "Economic recovery", "Trade agreements"],
        "JPY": ["Bank of Japan policy", "Export performance", "Safe haven demand", "Carry trade flows"],
        "SAR": ["Oil prices", "Saudi Vision 2030", "Regional stability", "USD peg"],
        "AED": ["Oil revenues", "Economic diversification", "Tourism sector", "Regional hub status"],
        "MAD": ["BAM policy", "Phosphate exports", "Tourism recovery", "Agricultural output"],
        "EGP": ["Central bank policy", "IMF program", "Tourism sector", "Suez Canal revenues"]
    }
    
    return factors_map.get(currency_code, ["Economic indicators", "Political stability", "Trade balance", "Monetary policy"])

def generate_mock_rate_data(currency: str, base_currency: str) -> Dict[str, Any]:
    """Generate mock rate data for demonstration"""
    import random
    
    # Mock base rates
    base_rates = {
        "USD": 10.25, "EUR": 11.15, "GBP": 12.85, "JPY": 0.068,
        "SAR": 2.73, "AED": 2.79, "EGP": 0.33, "TND": 3.25,
        "DZD": 0.076, "XOF": 0.017, "ZAR": 0.54, "NGN": 0.0067
    }
    
    base_rate = base_rates.get(currency, 1.0)
    
    # Add some variation
    variation = random.uniform(-0.05, 0.05)
    current_rate = base_rate * (1 + variation)
    
    # Mock 24h change
    change_24h = random.uniform(-0.02, 0.02) * current_rate
    
    return {
        "rate": current_rate,
        "change_24h": change_24h,
        "timestamp": datetime.now().isoformat()
    }