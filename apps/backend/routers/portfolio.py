from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import logging

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
        user_portfolios = mock_portfolios.get(current_user.id, [])
        return [{"id": "portfolio_1", "name": "My Portfolio", "description": "Main investment portfolio"}]
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
        portfolio_id = f"portfolio_{len(mock_portfolios) + 1}"
        new_portfolio = {
            "id": portfolio_id,
            "name": request.name,
            "description": request.description,
            "holdings": []
        }
        
        if current_user.id not in mock_portfolios:
            mock_portfolios[current_user.id] = {}
        
        mock_portfolios[current_user.id] = new_portfolio
        
        return {
            "id": portfolio_id,
            "name": request.name,
            "description": request.description,
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
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return user_portfolio.get("holdings", [])
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
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = user_portfolio.get("holdings", [])
        
        total_value = sum(holding.get("current_value", 0) for holding in holdings)
        total_cost = sum(holding.get("quantity", 0) * holding.get("purchase_price", 0) for holding in holdings)
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        return PortfolioSummary(
            total_value=total_value,
            total_cost=total_cost,
            total_gain_loss=total_gain_loss,
            total_gain_loss_percent=total_gain_loss_percent,
            holdings_count=len(holdings),
            last_updated=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio summary")

@router.post("/{portfolio_id}/holdings", response_model=PortfolioHolding)
async def add_holding(
    portfolio_id: str,
    request: AddHoldingRequest,
    current_user = Depends(get_current_user)
):
    """Add a new holding to the portfolio"""
    try:
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Mock current price (in real app, fetch from market data)
        current_price = request.purchase_price * 1.05  # Mock 5% gain
        
        new_holding = {
            "id": f"holding_{len(user_portfolio.get('holdings', [])) + 1}",
            "ticker": request.ticker,
            "name": f"{request.ticker} Company",  # Mock name
            "quantity": request.quantity,
            "purchase_price": request.purchase_price,
            "purchase_date": request.purchase_date or date.today(),
            "notes": request.notes,
            "current_price": current_price,
            "current_value": request.quantity * current_price,
            "total_gain_loss": request.quantity * (current_price - request.purchase_price),
            "total_gain_loss_percent": ((current_price - request.purchase_price) / request.purchase_price) * 100
        }
        
        if "holdings" not in user_portfolio:
            user_portfolio["holdings"] = []
        
        user_portfolio["holdings"].append(new_holding)
        
        return new_holding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding holding: {e}")
        raise HTTPException(status_code=500, detail="Failed to add holding")

@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=PortfolioHolding)
async def update_holding(
    portfolio_id: str,
    holding_id: str,
    request: UpdateHoldingRequest,
    current_user = Depends(get_current_user)
):
    """Update an existing holding"""
    try:
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = user_portfolio.get("holdings", [])
        holding_index = next((i for i, h in enumerate(holdings) if h.get("id") == holding_id), None)
        
        if holding_index is None:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        holding = holdings[holding_index]
        
        # Update fields if provided
        if request.quantity is not None:
            holding["quantity"] = request.quantity
        if request.purchase_price is not None:
            holding["purchase_price"] = request.purchase_price
        if request.purchase_date is not None:
            holding["purchase_date"] = request.purchase_date
        if request.notes is not None:
            holding["notes"] = request.notes
        
        # Recalculate values
        current_price = holding.get("current_price", holding["purchase_price"])
        holding["current_value"] = holding["quantity"] * current_price
        holding["total_gain_loss"] = holding["quantity"] * (current_price - holding["purchase_price"])
        holding["total_gain_loss_percent"] = ((current_price - holding["purchase_price"]) / holding["purchase_price"]) * 100
        
        return holding
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating holding: {e}")
        raise HTTPException(status_code=500, detail="Failed to update holding")

@router.delete("/{portfolio_id}/holdings/{holding_id}")
async def delete_holding(
    portfolio_id: str,
    holding_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a holding from the portfolio"""
    try:
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = user_portfolio.get("holdings", [])
        holding_index = next((i for i, h in enumerate(holdings) if h.get("id") == holding_id), None)
        
        if holding_index is None:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        # Remove the holding
        deleted_holding = holdings.pop(holding_index)
        
        return {
            "message": "Holding deleted successfully",
            "deleted_holding": deleted_holding
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting holding: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete holding")

@router.post("/{portfolio_id}/holdings/{holding_id}/adjust")
async def adjust_holding_quantity(
    portfolio_id: str,
    holding_id: str,
    adjustment: float,  # Positive for increase, negative for decrease
    current_user = Depends(get_current_user)
):
    """Adjust the quantity of a holding (add or remove shares)"""
    try:
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = user_portfolio.get("holdings", [])
        holding_index = next((i for i, h in enumerate(holdings) if h.get("id") == holding_id), None)
        
        if holding_index is None:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        holding = holdings[holding_index]
        new_quantity = holding["quantity"] + adjustment
        
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        
        if new_quantity == 0:
            # Remove the holding if quantity becomes zero
            deleted_holding = holdings.pop(holding_index)
            return {
                "message": "Holding removed (quantity adjusted to zero)",
                "deleted_holding": deleted_holding
            }
        
        # Update quantity and recalculate values
        holding["quantity"] = new_quantity
        current_price = holding.get("current_price", holding["purchase_price"])
        holding["current_value"] = holding["quantity"] * current_price
        holding["total_gain_loss"] = holding["quantity"] * (current_price - holding["purchase_price"])
        holding["total_gain_loss_percent"] = ((current_price - holding["purchase_price"]) / holding["purchase_price"]) * 100
        
        return {
            "message": "Holding quantity adjusted successfully",
            "updated_holding": holding
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting holding quantity: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust holding quantity")

@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(
    portfolio_id: str,
    period: str = "1M",  # 1D, 1W, 1M, 3M, 6M, 1Y, ALL
    current_user = Depends(get_current_user)
):
    """Get portfolio performance over time"""
    try:
        user_portfolio = mock_portfolios.get(current_user.id)
        if not user_portfolio or user_portfolio.get("id") != portfolio_id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Mock performance data (in real app, calculate from historical data)
        performance_data = {
            "period": period,
            "total_return": 7.25,
            "total_return_amount": 2711.25,
            "daily_returns": [
                {"date": "2024-01-01", "value": 100000, "return": 0},
                {"date": "2024-01-02", "value": 100500, "return": 0.5},
                {"date": "2024-01-03", "value": 101200, "return": 0.7},
                # Add more historical data points
            ],
            "volatility": 12.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": -3.2,
            "best_performing_holding": "ATW",
            "worst_performing_holding": "CIH"
        }
        
        return performance_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio performance") 