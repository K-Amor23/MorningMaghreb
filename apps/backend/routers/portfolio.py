from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date
import logging

# Import the enhanced portfolio service
from services.portfolio_service import portfolio_service, Trade, TradeType

# Configure logging
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models
class PortfolioHolding(BaseModel):
    id: Optional[str] = None
    ticker: str
    name: str
    quantity: float
    purchase_price: float
    purchase_date: Optional[date] = None
    notes: Optional[str] = None
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    total_gain_loss: Optional[float] = None
    total_gain_loss_percent: Optional[float] = None

class PortfolioSummary(BaseModel):
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings_count: int
    last_updated: datetime

class CreatePortfolioRequest(BaseModel):
    name: str
    description: Optional[str] = None
    initial_capital: Optional[float] = 100000.0

class UpdateHoldingRequest(BaseModel):
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None

class AddHoldingRequest(BaseModel):
    ticker: str
    quantity: float
    purchase_price: float
    purchase_date: Optional[date] = None
    notes: Optional[str] = None

class TradeRequest(BaseModel):
    ticker: str
    quantity: float
    price: float
    trade_type: str  # "buy" or "sell"
    date: date
    commission: Optional[float] = 0.0
    notes: Optional[str] = None

class BacktestRequest(BaseModel):
    trades: List[TradeRequest]
    initial_capital: float = 100000.0
    start_date: date
    end_date: date

class RiskMetrics(BaseModel):
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    beta: float

class PortfolioMetrics(BaseModel):
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    daily_pnl: float
    daily_pnl_percent: float
    positions_count: int
    cash_balance: float
    allocation_by_sector: Dict[str, float]
    risk_metrics: RiskMetrics

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

# Mock portfolio data (replace with database queries)
mock_portfolios = {
    "mock_user_id": {
        "id": "portfolio_1",
        "name": "My Portfolio",
        "description": "Main investment portfolio",
        "holdings": [
            {
                "id": "holding_1",
                "ticker": "ATW",
                "name": "Attijariwafa Bank",
                "quantity": 100,
                "purchase_price": 45.50,
                "purchase_date": date(2024, 1, 15),
                "notes": "Core banking position",
                "current_price": 48.75,
                "current_value": 4875.00,
                "total_gain_loss": 325.00,
                "total_gain_loss_percent": 7.14
            },
            {
                "id": "holding_2",
                "ticker": "BMCE",
                "name": "Bank of Africa",
                "quantity": 50,
                "purchase_price": 32.20,
                "purchase_date": date(2024, 2, 10),
                "notes": "Growth opportunity",
                "current_price": 35.80,
                "current_value": 1790.00,
                "total_gain_loss": 180.00,
                "total_gain_loss_percent": 11.18
            },
            {
                "id": "holding_3",
                "ticker": "CIH",
                "name": "CIH Bank",
                "quantity": 75,
                "purchase_price": 28.90,
                "purchase_date": date(2024, 3, 5),
                "notes": "Small cap exposure",
                "current_price": 31.25,
                "current_value": 2343.75,
                "total_gain_loss": 176.25,
                "total_gain_loss_percent": 8.13
            },
            {
                "id": "holding_4",
                "ticker": "IAM",
                "name": "Maroc Telecom",
                "quantity": 200,
                "purchase_price": 85.30,
                "purchase_date": date(2024, 1, 20),
                "notes": "Telecom leader",
                "current_price": 89.45,
                "current_value": 17890.00,
                "total_gain_loss": 830.00,
                "total_gain_loss_percent": 4.87
            }
        ]
    }
}

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_user_portfolios(current_user = Depends(get_current_user)):
    """Get all portfolios for the current user"""
    try:
        portfolios = portfolio_service.get_user_portfolios(current_user.id)
        return portfolios
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")

@router.post("/", response_model=dict)
async def create_portfolio(
    request: CreatePortfolioRequest,
    current_user = Depends(get_current_user)
):
    """Create a new portfolio"""
    try:
        portfolio = portfolio_service.create_portfolio(
            user_id=current_user.id,
            name=request.name,
            description=request.description
        )
        
        return {
            "id": portfolio['id'],
            "name": portfolio['name'],
            "description": portfolio['description'],
            "message": "Portfolio created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio")

@router.get("/{portfolio_id}/holdings", response_model=List[PortfolioHolding])
async def get_portfolio_holdings(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get all holdings for a specific portfolio"""
    try:
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Convert portfolio positions to holdings format
        holdings = []
        for ticker, trades in portfolio.get('positions', {}).items():
            if trades:
                position = portfolio_service.calculate_position_metrics(trades, portfolio_service.get_current_price(ticker) or 0)
                if position:
                    holdings.append({
                        "id": f"holding_{ticker}",
                        "ticker": position.ticker,
                        "name": f"{position.ticker} Company",
                        "quantity": position.quantity,
                        "purchase_price": position.avg_price,
                        "current_price": position.current_price,
                        "current_value": position.market_value,
                        "total_gain_loss": position.unrealized_pnl,
                        "total_gain_loss_percent": position.unrealized_pnl_percent
                    })
        
        return holdings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch holdings")

@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get portfolio summary with total values and performance"""
    try:
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        metrics = portfolio_service.calculate_portfolio_metrics(portfolio)
        
        return PortfolioSummary(
            total_value=metrics.total_value,
            total_cost=metrics.total_cost,
            total_gain_loss=metrics.total_pnl,
            total_gain_loss_percent=metrics.total_pnl_percent,
            holdings_count=metrics.positions_count,
            last_updated=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio summary")

@router.get("/{portfolio_id}/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get comprehensive portfolio metrics including risk metrics"""
    try:
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        metrics = portfolio_service.calculate_portfolio_metrics(portfolio)
        
        return PortfolioMetrics(
            total_value=metrics.total_value,
            total_cost=metrics.total_cost,
            total_pnl=metrics.total_pnl,
            total_pnl_percent=metrics.total_pnl_percent,
            daily_pnl=metrics.daily_pnl,
            daily_pnl_percent=metrics.daily_pnl_percent,
            positions_count=metrics.positions_count,
            cash_balance=metrics.cash_balance,
            allocation_by_sector=metrics.allocation_by_sector,
            risk_metrics=RiskMetrics(**metrics.risk_metrics)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio metrics")

@router.post("/{portfolio_id}/trades", response_model=dict)
async def add_trade(
    portfolio_id: str,
    request: TradeRequest,
    current_user = Depends(get_current_user)
):
    """Add a trade to the portfolio"""
    try:
        # Convert request to Trade object
        trade = Trade(
            date=request.date,
            ticker=request.ticker,
            quantity=request.quantity,
            price=request.price,
            trade_type=TradeType(request.trade_type),
            commission=request.commission,
            notes=request.notes
        )
        
        # Add trade to portfolio
        updated_portfolio = portfolio_service.add_trade(portfolio_id, trade)
        
        return {
            "message": "Trade added successfully",
            "portfolio_id": portfolio_id,
            "trade": {
                "ticker": trade.ticker,
                "quantity": trade.quantity,
                "price": trade.price,
                "trade_type": trade.trade_type.value,
                "date": trade.date.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding trade: {e}")
        raise HTTPException(status_code=500, detail="Failed to add trade")

@router.post("/backtest", response_model=dict)
async def run_backtest(
    request: BacktestRequest,
    current_user = Depends(get_current_user)
):
    """Run backtest simulation with historical trades"""
    try:
        # Convert requests to Trade objects
        trades = []
        for trade_req in request.trades:
            trade = Trade(
                date=trade_req.date,
                ticker=trade_req.ticker,
                quantity=trade_req.quantity,
                price=trade_req.price,
                trade_type=TradeType(trade_req.trade_type),
                commission=trade_req.commission,
                notes=trade_req.notes
            )
            trades.append(trade)
        
        # Run backtest
        results = portfolio_service.run_backtest(trades, request.initial_capital)
        
        return {
            "backtest_results": results,
            "message": "Backtest completed successfully"
        }
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail="Failed to run backtest")

@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(
    portfolio_id: str,
    period: str = "1M",  # 1D, 1W, 1M, 3M, 6M, 1Y, ALL
    current_user = Depends(get_current_user)
):
    """Get portfolio performance over time"""
    try:
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Calculate performance metrics
        metrics = portfolio_service.calculate_portfolio_metrics(portfolio)
        
        # Mock performance data (in real app, calculate from historical data)
        performance_data = {
            "period": period,
            "total_return": metrics.total_pnl_percent,
            "total_return_amount": metrics.total_pnl,
            "daily_returns": [
                {"date": "2024-01-01", "value": 100000, "return": 0},
                {"date": "2024-01-02", "value": 100500, "return": 0.5},
                {"date": "2024-01-03", "value": 101200, "return": 0.7},
                # Add more historical data points
            ],
            "volatility": metrics.risk_metrics['volatility'],
            "sharpe_ratio": metrics.risk_metrics['sharpe_ratio'],
            "max_drawdown": metrics.risk_metrics['max_drawdown'],
            "best_performing_holding": "ATW",
            "worst_performing_holding": "CIH"
        }
        
        return performance_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio performance")

@router.get("/{portfolio_id}/risk-analysis")
async def get_portfolio_risk_analysis(
    portfolio_id: str,
    current_user = Depends(get_current_user)
):
    """Get detailed risk analysis for the portfolio"""
    try:
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        metrics = portfolio_service.calculate_portfolio_metrics(portfolio)
        
        risk_analysis = {
            "portfolio_id": portfolio_id,
            "risk_metrics": metrics.risk_metrics,
            "sector_allocation": metrics.allocation_by_sector,
            "concentration_risk": calculate_concentration_risk(portfolio),
            "liquidity_analysis": calculate_liquidity_analysis(portfolio),
            "stress_test_results": run_stress_tests(portfolio)
        }
        
        return risk_analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch risk analysis")

def calculate_concentration_risk(self, portfolio: dict) -> dict:
    """Calculate concentration risk metrics"""
    # Mock implementation
    return {
        "largest_position_weight": 0.35,
        "top_5_positions_weight": 0.75,
        "sector_concentration": 0.45,
        "risk_level": "Medium"
    }

def calculate_liquidity_analysis(self, portfolio: dict) -> dict:
    """Calculate liquidity analysis"""
    # Mock implementation
    return {
        "average_daily_volume": 1500000,
        "liquidity_score": 0.8,
        "days_to_liquidate": 3.5,
        "liquidity_risk": "Low"
    }

def run_stress_tests(self, portfolio: dict) -> dict:
    """Run stress tests on portfolio"""
    # Mock implementation
    return {
        "market_crash_scenario": -12.5,
        "interest_rate_shock": -3.2,
        "sector_downturn": -8.7,
        "currency_devaluation": -5.1
    } 