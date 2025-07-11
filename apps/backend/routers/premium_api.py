from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/premium", tags=["Premium API"])

# Request/Response Models
class ApiKeyCreateRequest(BaseModel):
    key_name: str
    permissions: List[str] = ["read_financials", "read_macro", "read_quotes"]
    rate_limit_per_hour: Optional[int] = 1000
    expires_in_days: Optional[int] = 365

class ApiKeyResponse(BaseModel):
    id: str
    key_name: str
    api_key: str  # Only shown once on creation
    permissions: List[str]
    rate_limit_per_hour: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime

class FinancialDataRequest(BaseModel):
    tickers: List[str]
    metrics: List[str] = ["revenue", "net_income", "assets", "liabilities", "cash_flow"]
    period: Optional[str] = None  # "2024-Q1", "2024-Annual"
    gaap_only: bool = True

class MacroDataRequest(BaseModel):
    series_codes: List[str]
    start_date: str
    end_date: str
    frequency: Optional[str] = "monthly"

# Mock database functions (replace with actual Supabase calls)
async def get_user_by_api_key(api_key_hash: str) -> Optional[Dict[str, Any]]:
    """Get user by API key hash"""
    # Mock implementation - replace with actual database query
    if api_key_hash == "mock_hash":
        return {
            "id": "mock_user_id",
            "subscription_tier": "institutional",
            "api_key_id": "mock_api_key_id"
        }
    return None

async def check_rate_limit(api_key_id: str) -> bool:
    """Check if API key is within rate limit"""
    # Mock implementation - replace with actual rate limiting logic
    return True

async def log_api_usage(api_key_id: str, endpoint: str):
    """Log API usage for rate limiting"""
    # Mock implementation
    logger.info(f"API usage logged: {api_key_id} -> {endpoint}")

# Authentication dependency
async def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """Verify API key and return user info"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Hash the API key for lookup
    api_key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    
    user = await get_user_by_api_key(api_key_hash)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    if not await check_rate_limit(user["api_key_id"]):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return user

# API Key Management
@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    request: ApiKeyCreateRequest,
    user: dict = Depends(verify_api_key)
):
    """Create a new API key for premium access"""
    try:
        # Check if user has institutional tier
        if user["subscription_tier"] != "institutional":
            raise HTTPException(status_code=403, detail="Institutional tier required for API access")
        
        # Generate API key
        api_key = f"cas_sk_{secrets.token_urlsafe(32)}"
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        # Mock API key creation (replace with actual database insert)
        api_key_data = {
            "id": "mock_api_key_id",
            "key_name": request.key_name,
            "api_key": api_key,
            "permissions": request.permissions,
            "rate_limit_per_hour": request.rate_limit_per_hour,
            "is_active": True,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        return ApiKeyResponse(**api_key_data)
        
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@router.get("/api-keys", response_model=List[Dict[str, Any]])
async def list_api_keys(user: dict = Depends(verify_api_key)):
    """List all API keys for the user"""
    try:
        # Mock API keys list (replace with actual database query)
        api_keys = [
            {
                "id": "mock_key_1",
                "key_name": "Production API Key",
                "permissions": ["read_financials", "read_macro"],
                "is_active": True,
                "last_used": datetime.utcnow() - timedelta(hours=2),
                "created_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "id": "mock_key_2", 
                "key_name": "Development API Key",
                "permissions": ["read_quotes"],
                "is_active": True,
                "last_used": datetime.utcnow() - timedelta(days=5),
                "created_at": datetime.utcnow() - timedelta(days=60)
            }
        ]
        
        return api_keys
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")

# Premium Financial Data API
@router.post("/financials", response_model=Dict[str, Any])
async def get_gaap_financials(
    request: FinancialDataRequest,
    user: dict = Depends(verify_api_key)
):
    """Get GAAP-normalized financial data for specified companies"""
    try:
        # Log API usage
        await log_api_usage(user["api_key_id"], "financials")
        
        # Mock GAAP financial data
        financial_data = {}
        
        for ticker in request.tickers:
            # Mock company financial data
            company_data = {
                "ticker": ticker,
                "company_name": f"Mock Company {ticker}",
                "period": request.period or "2024-Q3",
                "gaap_data": {
                    "income_statement": {
                        "revenue": 50000000000 + hash(ticker) % 20000000000,
                        "net_income": 8000000000 + hash(ticker) % 4000000000,
                        "operating_income": 12000000000 + hash(ticker) % 6000000000,
                        "ebitda": 15000000000 + hash(ticker) % 8000000000
                    },
                    "balance_sheet": {
                        "total_assets": 200000000000 + hash(ticker) % 100000000000,
                        "total_liabilities": 120000000000 + hash(ticker) % 60000000000,
                        "total_equity": 80000000000 + hash(ticker) % 40000000000,
                        "cash_and_equivalents": 15000000000 + hash(ticker) % 8000000000
                    },
                    "cash_flow": {
                        "operating_cash_flow": 10000000000 + hash(ticker) % 5000000000,
                        "investing_cash_flow": -5000000000 + hash(ticker) % 3000000000,
                        "financing_cash_flow": -2000000000 + hash(ticker) % 2000000000,
                        "free_cash_flow": 8000000000 + hash(ticker) % 4000000000
                    }
                },
                "key_ratios": {
                    "roe": 15.0 + hash(ticker) % 10,
                    "roa": 8.0 + hash(ticker) % 5,
                    "debt_to_equity": 0.8 + (hash(ticker) % 10) / 10,
                    "current_ratio": 1.5 + (hash(ticker) % 10) / 10,
                    "pe_ratio": 12.0 + hash(ticker) % 8,
                    "pb_ratio": 1.2 + (hash(ticker) % 10) / 10
                },
                "gaap_adjustments": {
                    "ifrs_to_gaap_revenue_adjustment": 500000000 + hash(ticker) % 200000000,
                    "ifrs_to_gaap_net_income_adjustment": 100000000 + hash(ticker) % 50000000,
                    "adjustment_notes": "Converted from IFRS to US GAAP standards"
                }
            }
            
            financial_data[ticker] = company_data
        
        return {
            "data": financial_data,
            "metadata": {
                "total_companies": len(request.tickers),
                "period": request.period or "2024-Q3",
                "gaap_normalized": True,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting financial data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get financial data")

# Premium Macro Data API
@router.post("/macro", response_model=Dict[str, Any])
async def get_macro_data(
    request: MacroDataRequest,
    user: dict = Depends(verify_api_key)
):
    """Get macroeconomic time-series data"""
    try:
        # Log API usage
        await log_api_usage(user["api_key_id"], "macro")
        
        # Mock macro data
        macro_data = {}
        
        for series_code in request.series_codes:
            # Generate mock time-series data
            series_data = []
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            
            current_date = start_date
            while current_date <= end_date:
                # Generate realistic mock values based on series type
                if "cpi" in series_code.lower():
                    base_value = 120.0
                    variation = (hash(f"{series_code}{current_date}") % 20 - 10) / 100
                    value = base_value * (1 + variation)
                elif "gdp" in series_code.lower():
                    base_value = 1200000000000  # 1.2 trillion MAD
                    variation = (hash(f"{series_code}{current_date}") % 10 - 5) / 100
                    value = base_value * (1 + variation)
                elif "rate" in series_code.lower():
                    base_value = 3.0
                    variation = (hash(f"{series_code}{current_date}") % 10 - 5) / 100
                    value = base_value + variation
                else:
                    base_value = 100.0
                    variation = (hash(f"{series_code}{current_date}") % 20 - 10) / 100
                    value = base_value * (1 + variation)
                
                series_data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "value": round(value, 2),
                    "change": round(variation * 100, 2)
                })
                
                # Move to next period based on frequency
                if request.frequency == "daily":
                    current_date += timedelta(days=1)
                elif request.frequency == "weekly":
                    current_date += timedelta(weeks=1)
                elif request.frequency == "monthly":
                    current_date += timedelta(days=30)
                elif request.frequency == "quarterly":
                    current_date += timedelta(days=90)
                else:
                    current_date += timedelta(days=30)
            
            macro_data[series_code] = {
                "series_name": f"Mock {series_code.upper()} Series",
                "frequency": request.frequency,
                "unit": "MAD" if "gdp" in series_code.lower() else "Index",
                "data": series_data
            }
        
        return {
            "data": macro_data,
            "metadata": {
                "total_series": len(request.series_codes),
                "start_date": request.start_date,
                "end_date": request.end_date,
                "frequency": request.frequency,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting macro data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get macro data")

# API Usage Statistics
@router.get("/usage", response_model=Dict[str, Any])
async def get_api_usage(user: dict = Depends(verify_api_key)):
    """Get API usage statistics for the current period"""
    try:
        # Mock usage statistics
        usage_stats = {
            "current_period": {
                "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_requests": 15420,
                "requests_by_endpoint": {
                    "financials": 8230,
                    "macro": 4560,
                    "quotes": 2630
                },
                "rate_limit_remaining": 4580,
                "rate_limit_reset": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            },
            "historical": {
                "last_7_days": 3420,
                "last_30_days": 15420,
                "last_90_days": 45680
            }
        }
        
        return usage_stats
        
    except Exception as e:
        logger.error(f"Error getting API usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API usage") 