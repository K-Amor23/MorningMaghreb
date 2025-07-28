from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import the risk analytics service
from services.risk_analytics_service import (
    risk_analytics_service,
    RiskLevel,
    StressTestScenario
)

# Configure logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models
class RiskMetricsResponse(BaseModel):
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    cvar_95: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    calmar_ratio: float

class ConcentrationRiskResponse(BaseModel):
    largest_position_weight: float
    top_5_positions_weight: float
    sector_concentration: float
    geographic_concentration: float
    risk_level: str

class LiquidityRiskResponse(BaseModel):
    average_daily_volume: float
    liquidity_score: float
    days_to_liquidate: float
    bid_ask_spread: float
    risk_level: str

class StressTestResultResponse(BaseModel):
    scenario: str
    portfolio_loss: float
    portfolio_loss_percent: float
    worst_affected_positions: List[str]
    recovery_time_days: int
    risk_level: str

class RiskReportResponse(BaseModel):
    portfolio_id: str
    analysis_date: str
    overall_risk_level: str
    risk_metrics: RiskMetricsResponse
    concentration_risk: ConcentrationRiskResponse
    liquidity_risk: LiquidityRiskResponse
    stress_test_results: List[StressTestResultResponse]
    recommendations: List[str]

class WatchlistRiskRequest(BaseModel):
    tickers: List[str]

class WatchlistRiskResponse(BaseModel):
    watchlist_size: int
    total_market_cap: float
    sector_allocation: Dict[str, float]
    sector_concentration: float
    average_daily_volume: float
    average_volatility: float
    risk_level: str

# Mock token verification (replace with actual implementation)
async def verify_token(token: str):
    """Verify JWT token and return user info"""
    # Mock implementation - replace with actual token verification
    class MockUser:
        def __init__(self):
            self.id = "mock_user_id"
            self.subscription_tier = "pro"
    
    return MockUser()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    try:
        user = await verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

router = APIRouter()

@router.get("/portfolio/{portfolio_id}/risk-metrics", response_model=RiskMetricsResponse)
async def get_portfolio_risk_metrics(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get comprehensive risk metrics for a portfolio"""
    try:
        # Get portfolio data (this would come from portfolio service)
        portfolio = {
            'id': portfolio_id,
            'positions': {
                'ATW': {'market_value': 50000, 'quantity': 1000, 'avg_price': 50},
                'BMCE': {'market_value': 30000, 'quantity': 800, 'avg_price': 37.5},
                'CIH': {'market_value': 25000, 'quantity': 1000, 'avg_price': 25},
                'IAM': {'market_value': 40000, 'quantity': 450, 'avg_price': 88.9}
            },
            'total_value': 145000
        }
        
        risk_metrics = risk_analytics_service.calculate_risk_metrics(portfolio)
        
        return RiskMetricsResponse(
            volatility=risk_metrics.volatility,
            sharpe_ratio=risk_metrics.sharpe_ratio,
            sortino_ratio=risk_metrics.sortino_ratio,
            max_drawdown=risk_metrics.max_drawdown,
            var_95=risk_metrics.var_95,
            var_99=risk_metrics.var_99,
            cvar_95=risk_metrics.cvar_95,
            beta=risk_metrics.beta,
            alpha=risk_metrics.alpha,
            information_ratio=risk_metrics.information_ratio,
            treynor_ratio=risk_metrics.treynor_ratio,
            calmar_ratio=risk_metrics.calmar_ratio
        )
    except Exception as e:
        logger.error(f"Error getting portfolio risk metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get portfolio risk metrics")

@router.get("/portfolio/{portfolio_id}/concentration-risk", response_model=ConcentrationRiskResponse)
async def get_portfolio_concentration_risk(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get concentration risk analysis for a portfolio"""
    try:
        # Get portfolio data
        portfolio = {
            'id': portfolio_id,
            'positions': {
                'ATW': {'market_value': 50000, 'quantity': 1000, 'avg_price': 50},
                'BMCE': {'market_value': 30000, 'quantity': 800, 'avg_price': 37.5},
                'CIH': {'market_value': 25000, 'quantity': 1000, 'avg_price': 25},
                'IAM': {'market_value': 40000, 'quantity': 450, 'avg_price': 88.9}
            },
            'total_value': 145000
        }
        
        concentration_risk = risk_analytics_service.calculate_concentration_risk(portfolio)
        
        return ConcentrationRiskResponse(
            largest_position_weight=concentration_risk.largest_position_weight,
            top_5_positions_weight=concentration_risk.top_5_positions_weight,
            sector_concentration=concentration_risk.sector_concentration,
            geographic_concentration=concentration_risk.geographic_concentration,
            risk_level=concentration_risk.risk_level.value
        )
    except Exception as e:
        logger.error(f"Error getting concentration risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to get concentration risk")

@router.get("/portfolio/{portfolio_id}/liquidity-risk", response_model=LiquidityRiskResponse)
async def get_portfolio_liquidity_risk(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get liquidity risk analysis for a portfolio"""
    try:
        # Get portfolio data
        portfolio = {
            'id': portfolio_id,
            'positions': {
                'ATW': {'market_value': 50000, 'quantity': 1000, 'avg_price': 50},
                'BMCE': {'market_value': 30000, 'quantity': 800, 'avg_price': 37.5},
                'CIH': {'market_value': 25000, 'quantity': 1000, 'avg_price': 25},
                'IAM': {'market_value': 40000, 'quantity': 450, 'avg_price': 88.9}
            },
            'total_value': 145000
        }
        
        liquidity_risk = risk_analytics_service.calculate_liquidity_risk(portfolio)
        
        return LiquidityRiskResponse(
            average_daily_volume=liquidity_risk.average_daily_volume,
            liquidity_score=liquidity_risk.liquidity_score,
            days_to_liquidate=liquidity_risk.days_to_liquidate,
            bid_ask_spread=liquidity_risk.bid_ask_spread,
            risk_level=liquidity_risk.risk_level.value
        )
    except Exception as e:
        logger.error(f"Error getting liquidity risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to get liquidity risk")

@router.get("/portfolio/{portfolio_id}/stress-tests", response_model=List[StressTestResultResponse])
async def get_portfolio_stress_tests(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get stress test results for a portfolio"""
    try:
        # Get portfolio data
        portfolio = {
            'id': portfolio_id,
            'positions': {
                'ATW': {'market_value': 50000, 'quantity': 1000, 'avg_price': 50},
                'BMCE': {'market_value': 30000, 'quantity': 800, 'avg_price': 37.5},
                'CIH': {'market_value': 25000, 'quantity': 1000, 'avg_price': 25},
                'IAM': {'market_value': 40000, 'quantity': 450, 'avg_price': 88.9}
            },
            'total_value': 145000
        }
        
        stress_test_results = risk_analytics_service.run_stress_tests(portfolio)
        
        return [
            StressTestResultResponse(
                scenario=result.scenario.value,
                portfolio_loss=result.portfolio_loss,
                portfolio_loss_percent=result.portfolio_loss_percent,
                worst_affected_positions=result.worst_affected_positions,
                recovery_time_days=result.recovery_time_days,
                risk_level=result.risk_level.value
            )
            for result in stress_test_results
        ]
    except Exception as e:
        logger.error(f"Error getting stress test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stress test results")

@router.get("/portfolio/{portfolio_id}/risk-report", response_model=RiskReportResponse)
async def get_portfolio_risk_report(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get comprehensive risk report for a portfolio"""
    try:
        # Get portfolio data
        portfolio = {
            'id': portfolio_id,
            'positions': {
                'ATW': {'market_value': 50000, 'quantity': 1000, 'avg_price': 50},
                'BMCE': {'market_value': 30000, 'quantity': 800, 'avg_price': 37.5},
                'CIH': {'market_value': 25000, 'quantity': 1000, 'avg_price': 25},
                'IAM': {'market_value': 40000, 'quantity': 450, 'avg_price': 88.9}
            },
            'total_value': 145000
        }
        
        risk_report = risk_analytics_service.generate_risk_report(portfolio)
        
        if not risk_report:
            raise HTTPException(status_code=500, detail="Failed to generate risk report")
        
        return RiskReportResponse(
            portfolio_id=risk_report['portfolio_id'],
            analysis_date=risk_report['analysis_date'],
            overall_risk_level=risk_report['overall_risk_level'],
            risk_metrics=RiskMetricsResponse(**risk_report['risk_metrics']),
            concentration_risk=ConcentrationRiskResponse(**risk_report['concentration_risk']),
            liquidity_risk=LiquidityRiskResponse(**risk_report['liquidity_risk']),
            stress_test_results=[
                StressTestResultResponse(**result) for result in risk_report['stress_test_results']
            ],
            recommendations=risk_report['recommendations']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk report")

@router.post("/watchlist/risk-analysis", response_model=WatchlistRiskResponse)
async def analyze_watchlist_risk(
    request: WatchlistRiskRequest,
    current_user = Depends(get_current_user)
):
    """Analyze risk metrics for a watchlist"""
    try:
        risk_analysis = risk_analytics_service.analyze_watchlist_risk(request.tickers)
        
        if not risk_analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze watchlist risk")
        
        return WatchlistRiskResponse(
            watchlist_size=risk_analysis['watchlist_size'],
            total_market_cap=risk_analysis['total_market_cap'],
            sector_allocation=risk_analysis['sector_allocation'],
            sector_concentration=risk_analysis['sector_concentration'],
            average_daily_volume=risk_analysis['average_daily_volume'],
            average_volatility=risk_analysis['average_volatility'],
            risk_level=risk_analysis['risk_level']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing watchlist risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze watchlist risk")

@router.get("/market/risk-indicators")
async def get_market_risk_indicators(current_user = Depends(get_current_user)):
    """Get market-wide risk indicators"""
    try:
        # Mock market risk indicators
        market_indicators = {
            "masi_volatility": 0.18,  # 18% annualized volatility
            "market_beta": 1.0,
            "market_correlation": 0.75,
            "sector_rotation": {
                "banking": 0.35,
                "telecommunications": 0.25,
                "mining": 0.15,
                "energy": 0.10,
                "real_estate": 0.08,
                "insurance": 0.07
            },
            "liquidity_indicators": {
                "average_daily_volume": 2500000,
                "bid_ask_spread_avg": 0.0015,
                "market_depth": 0.8
            },
            "risk_level": "medium",
            "last_updated": datetime.now().isoformat()
        }
        
        return market_indicators
    except Exception as e:
        logger.error(f"Error getting market risk indicators: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market risk indicators")

@router.get("/portfolio/{portfolio_id}/correlation-matrix")
async def get_portfolio_correlation_matrix(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get correlation matrix for portfolio positions"""
    try:
        # Mock correlation matrix
        tickers = ['ATW', 'BMCE', 'CIH', 'IAM']
        correlation_matrix = {
            "tickers": tickers,
            "matrix": [
                [1.00, 0.65, 0.70, 0.45],
                [0.65, 1.00, 0.75, 0.50],
                [0.70, 0.75, 1.00, 0.55],
                [0.45, 0.50, 0.55, 1.00]
            ],
            "average_correlation": 0.61,
            "diversification_score": 0.39,  # 1 - average_correlation
            "last_updated": datetime.now().isoformat()
        }
        
        return correlation_matrix
    except Exception as e:
        logger.error(f"Error getting correlation matrix: {e}")
        raise HTTPException(status_code=500, detail="Failed to get correlation matrix")

@router.get("/portfolio/{portfolio_id}/performance-attribution")
async def get_portfolio_performance_attribution(
    portfolio_id: str,
    period: str = "1M",  # 1M, 3M, 6M, 1Y
    current_user = Depends(get_current_user)
):
    """Get performance attribution analysis"""
    try:
        # Mock performance attribution
        attribution = {
            "period": period,
            "total_return": 0.085,  # 8.5%
            "benchmark_return": 0.065,  # 6.5%
            "excess_return": 0.020,  # 2.0%
            "attribution_breakdown": {
                "asset_allocation": 0.008,
                "stock_selection": 0.012,
                "interaction": 0.000
            },
            "sector_contributions": {
                "banking": 0.045,
                "telecommunications": 0.025,
                "mining": 0.010,
                "energy": 0.005
            },
            "top_contributors": [
                {"ticker": "ATW", "contribution": 0.025},
                {"ticker": "IAM", "contribution": 0.020},
                {"ticker": "BMCE", "contribution": 0.015}
            ],
            "bottom_contributors": [
                {"ticker": "CIH", "contribution": 0.005},
                {"ticker": "MNG", "contribution": 0.003}
            ]
        }
        
        return attribution
    except Exception as e:
        logger.error(f"Error getting performance attribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance attribution")

@router.get("/portfolio/{portfolio_id}/risk-decomposition")
async def get_portfolio_risk_decomposition(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get risk decomposition analysis"""
    try:
        # Mock risk decomposition
        risk_decomposition = {
            "total_risk": 0.15,  # 15% annualized volatility
            "risk_decomposition": {
                "systematic_risk": 0.10,  # 66.7%
                "idiosyncratic_risk": 0.05,  # 33.3%
                "factor_risk": 0.08,  # 53.3%
                "residual_risk": 0.07  # 46.7%
            },
            "factor_exposures": {
                "market_factor": 0.85,
                "size_factor": -0.15,
                "value_factor": 0.25,
                "momentum_factor": 0.10
            },
            "risk_contributors": [
                {"ticker": "ATW", "risk_contribution": 0.045},
                {"ticker": "BMCE", "risk_contribution": 0.035},
                {"ticker": "CIH", "risk_contribution": 0.030},
                {"ticker": "IAM", "risk_contribution": 0.040}
            ]
        }
        
        return risk_decomposition
    except Exception as e:
        logger.error(f"Error getting risk decomposition: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk decomposition") 