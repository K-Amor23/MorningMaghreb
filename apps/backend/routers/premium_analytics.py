"""
Premium Analytics Router
Handles ML-based signals, portfolio optimization, and predictive models
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.connection import get_db
from services.premium_analytics_service import PremiumAnalyticsService
from utils.auth import get_current_user

router = APIRouter()
security = HTTPBearer()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PortfolioOptimizationRequest(BaseModel):
    tickers: List[str]
    target_return: Optional[float] = None
    risk_tolerance: float = 0.5
    constraints: Optional[Dict[str, Any]] = None

class BlackLittermanRequest(BaseModel):
    tickers: List[str]
    views: List[Dict[str, Any]]  # [{"ticker": "ATW", "expected_return": 0.15, "confidence": 0.8}]
    risk_aversion: float = 2.5
    tau: float = 0.05

class PricePredictionRequest(BaseModel):
    ticker: str
    prediction_horizon: int = 30
    confidence_threshold: float = 0.7

# ============================================================================
# ML MODEL MANAGEMENT
# ============================================================================

@router.post("/models")
async def create_ml_model(
    model_name: str,
    model_type: str,
    version: str,
    hyperparameters: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new ML model (Admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.create_ml_model(
        model_name, model_type, version, hyperparameters
    )

@router.put("/models/{model_id}/status")
async def update_model_status(
    model_id: str,
    status: str,
    accuracy_score: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ML model status (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.update_model_status(model_id, status, accuracy_score)

@router.get("/models")
async def get_active_models(
    model_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get active ML models"""
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.get_active_models(model_type)

# ============================================================================
# PREDICTIVE MODELS
# ============================================================================

@router.post("/predictions/price")
async def generate_price_prediction(
    request: PricePredictionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate price prediction for a ticker"""
    # Check premium subscription
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.generate_price_prediction(
        request.ticker, request.prediction_horizon, request.confidence_threshold
    )

@router.post("/predictions/volatility")
async def generate_volatility_forecast(
    ticker: str,
    forecast_days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate volatility forecast for a ticker"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.generate_volatility_forecast(ticker, forecast_days)

# ============================================================================
# PORTFOLIO OPTIMIZATION
# ============================================================================

@router.post("/optimization/markowitz")
async def optimize_portfolio_markowitz(
    request: PortfolioOptimizationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize portfolio using Markowitz mean-variance optimization"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.optimize_portfolio_markowitz(
        current_user["id"],
        request.tickers,
        request.target_return,
        request.risk_tolerance,
        request.constraints
    )

@router.post("/optimization/black-litterman")
async def optimize_portfolio_black_litterman(
    request: BlackLittermanRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize portfolio using Black-Litterman model"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.optimize_portfolio_black_litterman(
        current_user["id"],
        request.tickers,
        request.views,
        request.risk_aversion,
        request.tau
    )

@router.get("/optimizations")
async def get_user_optimizations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolio optimizations"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    return await analytics_service.get_user_optimizations(current_user["id"])

# ============================================================================
# ANALYTICS DASHBOARD
# ============================================================================

@router.get("/dashboard/overview")
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get premium analytics dashboard overview"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    
    # Get user's recent optimizations
    optimizations = await analytics_service.get_user_optimizations(current_user["id"])
    
    # Get active models
    active_models = await analytics_service.get_active_models()
    
    return {
        "user_id": current_user["id"],
        "subscription_tier": current_user.get("subscription_tier"),
        "recent_optimizations": optimizations[:5],  # Last 5 optimizations
        "active_models": active_models,
        "available_features": [
            "price_predictions",
            "volatility_forecasts",
            "markowitz_optimization",
            "black_litterman_optimization",
            "ml_signals"
        ]
    }

@router.get("/signals/{ticker}")
async def get_ml_signals(
    ticker: str,
    signal_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ML-based signals for a ticker"""
    if current_user.get("subscription_tier") not in ["pro", "institutional"]:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
    analytics_service = PremiumAnalyticsService(db)
    
    # Generate signals based on available models
    signals = {}
    
    # Price prediction signal
    try:
        price_prediction = await analytics_service.generate_price_prediction(ticker)
        signals["price_prediction"] = price_prediction
    except Exception as e:
        signals["price_prediction"] = {"error": str(e)}
    
    # Volatility forecast signal
    try:
        volatility_forecast = await analytics_service.generate_volatility_forecast(ticker)
        signals["volatility_forecast"] = volatility_forecast
    except Exception as e:
        signals["volatility_forecast"] = {"error": str(e)}
    
    return {
        "ticker": ticker,
        "signals": signals,
        "generated_at": datetime.now().isoformat()
    } 