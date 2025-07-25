from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import random

from models.market import Quote, HistoricalData, MarketSummary
from utils.auth import get_current_user
from utils.cache import cache_response

router = APIRouter()

# Mock CSE data - in production, this would fetch from real API/database
MOCK_QUOTES = [
    {"ticker": "MASI", "name": "MASI Index", "price": 13456.78, "change": 2.34, "change_percent": 0.017},
    {"ticker": "MADEX", "name": "MADEX Index", "price": 11234.56, "change": -1.23, "change_percent": -0.011},
    {"ticker": "MASI-ESG", "name": "MASI ESG Index", "price": 987.65, "change": 0.98, "change_percent": 0.001},
    {"ticker": "ATW", "name": "Attijariwafa Bank", "price": 534.50, "change": 4.50, "change_percent": 0.008},
    {"ticker": "IAM", "name": "Maroc Telecom", "price": 156.30, "change": -2.10, "change_percent": -0.013},
    {"ticker": "BCP", "name": "Banque Centrale Populaire", "price": 268.60, "change": 8.10, "change_percent": 0.031},
    {"ticker": "BMCE", "name": "BMCE Bank", "price": 187.40, "change": -0.90, "change_percent": -0.005},
    {"ticker": "ONA", "name": "Omnium Nord Africain", "price": 456.20, "change": 3.40, "change_percent": 0.0075},
]

@router.get("/quotes", response_model=List[Quote])
async def get_quotes(
    tickers: Optional[str] = Query(None, description="Comma-separated list of tickers"),
    user=Depends(get_current_user)
):
    """Get real-time market quotes"""
    try:
        # Filter by tickers if provided
        if tickers:
            ticker_list = [t.strip().upper() for t in tickers.split(",")]
            filtered_quotes = [q for q in MOCK_QUOTES if q["ticker"] in ticker_list]
        else:
            filtered_quotes = MOCK_QUOTES
        
        # Simulate real-time price fluctuations
        live_quotes = []
        for quote in filtered_quotes:
            # Add some random variation to prices
            price_change = (random.random() - 0.5) * 2
            live_quote = Quote(
                ticker=quote["ticker"],
                name=quote["name"],
                price=quote["price"] + price_change,
                change=quote["change"] + (random.random() - 0.5) * 0.5,
                change_percent=quote["change_percent"] + (random.random() - 0.5) * 0.001,
                volume=random.randint(10000, 1000000),
                timestamp=datetime.now()
            )
            live_quotes.append(live_quote)
        
        return live_quotes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quotes: {str(e)}")

@router.get("/history/{ticker}")
async def get_historical_data(
    ticker: str,
    period: str = Query("1M", description="Time period: 1D, 1W, 1M, 3M, 6M, 1Y, 5Y"),
    user=Depends(get_current_user)
):
    """Get historical market data for a ticker"""
    try:
        # Calculate date range based on period
        end_date = datetime.now()
        if period == "1D":
            start_date = end_date - timedelta(days=1)
        elif period == "1W":
            start_date = end_date - timedelta(weeks=1)
        elif period == "1M":
            start_date = end_date - timedelta(days=30)
        elif period == "3M":
            start_date = end_date - timedelta(days=90)
        elif period == "6M":
            start_date = end_date - timedelta(days=180)
        elif period == "1Y":
            start_date = end_date - timedelta(days=365)
        elif period == "5Y":
            start_date = end_date - timedelta(days=1825)
        else:
            raise HTTPException(status_code=400, detail="Invalid period")
        
        # Generate mock historical data
        historical_data = []
        current_date = start_date
        base_price = 100
        
        while current_date <= end_date:
            # Simulate price movement
            price_change = (random.random() - 0.5) * 0.02
            base_price *= (1 + price_change)
            
            data_point = HistoricalData(
                ticker=ticker.upper(),
                date=current_date,
                open=base_price,
                high=base_price * 1.02,
                low=base_price * 0.98,
                close=base_price,
                volume=random.randint(50000, 500000)
            )
            historical_data.append(data_point)
            
            # Increment date
            if period == "1D":
                current_date += timedelta(minutes=30)
            else:
                current_date += timedelta(days=1)
        
        return historical_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@router.get("/summary", response_model=MarketSummary)
async def get_market_summary(user=Depends(get_current_user)):
    """Get market summary with key indices and stats"""
    try:
        # Calculate market summary from current quotes
        quotes = await get_quotes(user=user)
        
        # Find key indices
        masi = next((q for q in quotes if q.ticker == "MASI"), None)
        madex = next((q for q in quotes if q.ticker == "MADEX"), None)
        masi_esg = next((q for q in quotes if q.ticker == "MASI-ESG"), None)
        
        # Calculate market stats
        positive_movers = len([q for q in quotes if q.change > 0])
        negative_movers = len([q for q in quotes if q.change < 0])
        total_volume = sum(q.volume for q in quotes)
        
        # Find top gainers and losers
        top_gainers = sorted(quotes, key=lambda x: x.change_percent, reverse=True)[:3]
        top_losers = sorted(quotes, key=lambda x: x.change_percent)[:3]
        
        summary = MarketSummary(
            masi_index=masi.price if masi else 0,
            masi_change=masi.change_percent if masi else 0,
            madex_index=madex.price if madex else 0,
            madex_change=madex.change_percent if madex else 0,
            masi_esg_index=masi_esg.price if masi_esg else 0,
            masi_esg_change=masi_esg.change_percent if masi_esg else 0,
            positive_movers=positive_movers,
            negative_movers=negative_movers,
            total_volume=total_volume,
            top_gainers=top_gainers,
            top_losers=top_losers,
            timestamp=datetime.now()
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating market summary: {str(e)}")

@router.get("/sectors")
async def get_sector_performance(user=Depends(get_current_user)):
    """Get sector performance data"""
    try:
        # Mock sector data
        sectors = [
            {"name": "Banks", "change_percent": 0.85, "volume": 2500000},
            {"name": "Telecoms", "change_percent": -0.23, "volume": 1200000},
            {"name": "Insurance", "change_percent": 1.12, "volume": 850000},
            {"name": "Real Estate", "change_percent": -0.45, "volume": 650000},
            {"name": "Mining", "change_percent": 2.34, "volume": 1800000},
            {"name": "Energy", "change_percent": 0.67, "volume": 980000},
        ]
        
        return sectors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector data: {str(e)}")

@router.get("/watchlist")
async def get_watchlist(user=Depends(get_current_user)):
    """Get user's watchlist"""
    try:
        # TODO: Fetch from database based on user ID
        # For now, return mock data
        watchlist_tickers = ["ATW", "IAM", "BCP", "BMCE"]
        watchlist_quotes = await get_quotes(tickers=",".join(watchlist_tickers), user=user)
        
        return watchlist_quotes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching watchlist: {str(e)}")

@router.get("/watchlist/public")
async def get_public_watchlist():
    """Get public watchlist (no authentication required)"""
    try:
        # Return mock watchlist data for public access
        watchlist_tickers = ["ATW", "IAM", "BCP", "BMCE"]
        
        # Create mock quotes for watchlist
        mock_quotes = []
        for ticker in watchlist_tickers:
            mock_quotes.append({
                "ticker": ticker,
                "name": f"{ticker} Company",
                "price": 100 + (hash(ticker) % 50),  # Generate consistent mock price
                "change": (hash(ticker) % 10) - 5,   # Generate mock change
                "change_percent": ((hash(ticker) % 10) - 5) * 0.5,  # Generate mock change percent
                "volume": 1000000 + (hash(ticker) % 500000),
                "high": 105 + (hash(ticker) % 10),
                "low": 95 + (hash(ticker) % 10),
                "open": 100 + (hash(ticker) % 5),
                "close": 100 + (hash(ticker) % 50),
                "timestamp": "2024-01-01T00:00:00Z"
            })
        
        return mock_quotes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching watchlist: {str(e)}")

@router.post("/watchlist/{ticker}")
async def add_to_watchlist(ticker: str, user=Depends(get_current_user)):
    """Add ticker to user's watchlist"""
    try:
        # TODO: Add to database
        return {"message": f"Added {ticker} to watchlist"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to watchlist: {str(e)}")

@router.post("/watchlist/public/{ticker}")
async def add_to_public_watchlist(ticker: str):
    """Add ticker to public watchlist (no authentication required)"""
    try:
        # Mock implementation - in real app this would store in session/localStorage
        return {"message": f"Added {ticker} to watchlist", "ticker": ticker}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to watchlist: {str(e)}")

@router.delete("/watchlist/{ticker}")
async def remove_from_watchlist(ticker: str, user=Depends(get_current_user)):
    """Remove ticker from user's watchlist"""
    try:
        # TODO: Remove from database
        return {"message": f"Removed {ticker} from watchlist"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing from watchlist: {str(e)}")

@router.delete("/watchlist/public/{ticker}")
async def remove_from_public_watchlist(ticker: str):
    """Remove ticker from public watchlist (no authentication required)"""
    try:
        # Mock implementation
        return {"message": f"Removed {ticker} from watchlist", "ticker": ticker}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing from watchlist: {str(e)}")