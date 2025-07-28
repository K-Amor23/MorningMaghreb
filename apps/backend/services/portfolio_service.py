#!/usr/bin/env python3
"""
Enhanced Portfolio Service with Backtesting Engine

Features:
- CRUD operations for portfolios and holdings
- Real-time P/L calculation
- Historical backtesting engine
- Risk metrics calculation
- Performance analytics
- Integration with OHLCV data
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import asyncio
from dataclasses import dataclass
from enum import Enum

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portfolio_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradeType(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    date: date
    ticker: str
    quantity: float
    price: float
    trade_type: TradeType
    commission: float = 0.0
    notes: Optional[str] = None

@dataclass
class Position:
    ticker: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    cost_basis: float
    last_updated: datetime

@dataclass
class PortfolioMetrics:
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    daily_pnl: float
    daily_pnl_percent: float
    positions_count: int
    cash_balance: float
    allocation_by_sector: Dict[str, float]
    risk_metrics: Dict[str, float]

class PortfolioService:
    """Enhanced portfolio service with backtesting capabilities"""
    
    def __init__(self):
        # Supabase client
        self.supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if self.supabase_url and self.supabase_service_key:
            self.supabase = create_client(self.supabase_url, self.supabase_service_key)
            logger.info("✅ Supabase client initialized")
        else:
            self.supabase = None
            logger.warning("⚠️  Supabase credentials not found")
        
        # OHLCV data path
        self.ohlcv_path = Path("etl/data/ohlcv")
        
        # Commission rate (0.1% default)
        self.commission_rate = 0.001
        
        logger.info("✅ Portfolio Service initialized")
    
    def load_ohlcv_data(self, ticker: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """Load OHLCV data for a specific ticker and date range"""
        try:
            file_path = self.ohlcv_path / f"{ticker}_ohlcv_90days.csv"
            if not file_path.exists():
                logger.warning(f"OHLCV file not found for {ticker}")
                return None
            
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
            df = df.sort_values('date')
            
            return df
        except Exception as e:
            logger.error(f"Error loading OHLCV data for {ticker}: {e}")
            return None
    
    def calculate_position_metrics(self, trades: List[Trade], current_price: float) -> Position:
        """Calculate position metrics from trades"""
        if not trades:
            return None
        
        # Calculate average price and total quantity
        total_quantity = 0
        total_cost = 0
        total_commission = 0
        
        for trade in trades:
            if trade.trade_type == TradeType.BUY:
                total_quantity += trade.quantity
                total_cost += trade.quantity * trade.price
                total_commission += trade.commission
            else:  # SELL
                total_quantity -= trade.quantity
                total_cost -= trade.quantity * trade.price
                total_commission += trade.commission
        
        if total_quantity <= 0:
            return None
        
        avg_price = total_cost / total_quantity
        market_value = total_quantity * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_percent = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return Position(
            ticker=trades[0].ticker,
            quantity=total_quantity,
            avg_price=avg_price,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_percent=unrealized_pnl_percent,
            cost_basis=total_cost,
            last_updated=datetime.now()
        )
    
    def simulate_trade(self, portfolio: Dict, trade: Trade) -> Dict:
        """Simulate a trade and update portfolio"""
        ticker = trade.ticker
        
        # Get current price from OHLCV data
        current_price = self.get_current_price(ticker)
        if current_price is None:
            current_price = trade.price  # Use trade price as fallback
        
        # Update portfolio
        if ticker not in portfolio['positions']:
            portfolio['positions'][ticker] = []
        
        portfolio['positions'][ticker].append(trade)
        
        # Recalculate position metrics
        position = self.calculate_position_metrics(portfolio['positions'][ticker], current_price)
        
        # Update cash balance
        if trade.trade_type == TradeType.BUY:
            portfolio['cash_balance'] -= (trade.quantity * trade.price + trade.commission)
        else:
            portfolio['cash_balance'] += (trade.quantity * trade.price - trade.commission)
        
        return portfolio
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for a ticker"""
        try:
            file_path = self.ohlcv_path / f"{ticker}_ohlcv_90days.csv"
            if not file_path.exists():
                return None
            
            df = pd.read_csv(file_path)
            # Get the latest close price
            latest_price = df['close'].iloc[-1]
            return latest_price
        except Exception as e:
            logger.error(f"Error getting current price for {ticker}: {e}")
            return None
    
    def calculate_portfolio_metrics(self, portfolio: Dict) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        total_value = portfolio['cash_balance']
        total_cost = 0
        positions_count = 0
        allocation_by_sector = {}
        
        for ticker, trades in portfolio['positions'].items():
            if not trades:
                continue
            
            current_price = self.get_current_price(ticker)
            if current_price is None:
                continue
            
            position = self.calculate_position_metrics(trades, current_price)
            if position is None:
                continue
            
            total_value += position.market_value
            total_cost += position.cost_basis
            positions_count += 1
            
            # Calculate sector allocation (mock for now)
            sector = self.get_company_sector(ticker)
            if sector:
                allocation_by_sector[sector] = allocation_by_sector.get(sector, 0) + position.market_value
        
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # Calculate risk metrics
        risk_metrics = self.calculate_risk_metrics(portfolio)
        
        return PortfolioMetrics(
            total_value=total_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            daily_pnl=0,  # Would need historical data
            daily_pnl_percent=0,
            positions_count=positions_count,
            cash_balance=portfolio['cash_balance'],
            allocation_by_sector=allocation_by_sector,
            risk_metrics=risk_metrics
        )
    
    def calculate_risk_metrics(self, portfolio: Dict) -> Dict[str, float]:
        """Calculate risk metrics for the portfolio"""
        try:
            # Calculate volatility, beta, Sharpe ratio, etc.
            returns = self.calculate_portfolio_returns(portfolio)
            
            if len(returns) < 2:
                return {
                    'volatility': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'var_95': 0.0,
                    'beta': 1.0
                }
            
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            avg_return = np.mean(returns) * 252  # Annualized
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
            
            # Calculate max drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Calculate Value at Risk (95% confidence)
            var_95 = np.percentile(returns, 5)
            
            return {
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'beta': 1.0  # Would need market data for actual beta
            }
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0,
                'beta': 1.0
            }
    
    def calculate_portfolio_returns(self, portfolio: Dict) -> List[float]:
        """Calculate historical portfolio returns"""
        # This would need historical price data for all positions
        # For now, return mock data
        return [0.01, -0.005, 0.02, -0.01, 0.015]  # Mock returns
    
    def get_company_sector(self, ticker: str) -> Optional[str]:
        """Get company sector (mock implementation)"""
        sector_mapping = {
            'ATW': 'Banking',
            'BMCE': 'Banking',
            'CIH': 'Banking',
            'BCP': 'Banking',
            'IAM': 'Telecommunications',
            'CTM': 'Telecommunications',
            'MNG': 'Mining',
            'GAZ': 'Energy',
            'LES': 'Real Estate',
            'WAA': 'Insurance'
        }
        return sector_mapping.get(ticker, 'Other')
    
    def run_backtest(self, trades: List[Trade], initial_capital: float = 100000) -> Dict[str, Any]:
        """Run backtest simulation with historical trades"""
        try:
            # Initialize portfolio
            portfolio = {
                'cash_balance': initial_capital,
                'positions': {},
                'trades': trades
            }
            
            # Sort trades by date
            sorted_trades = sorted(trades, key=lambda x: x.date)
            
            # Simulate each trade
            for trade in sorted_trades:
                portfolio = self.simulate_trade(portfolio, trade)
            
            # Calculate final metrics
            final_metrics = self.calculate_portfolio_metrics(portfolio)
            
            # Calculate performance over time
            performance_history = self.calculate_performance_history(portfolio, sorted_trades)
            
            return {
                'initial_capital': initial_capital,
                'final_value': final_metrics.total_value,
                'total_return': final_metrics.total_pnl,
                'total_return_percent': final_metrics.total_pnl_percent,
                'final_metrics': final_metrics,
                'performance_history': performance_history,
                'trades_count': len(trades),
                'positions_count': final_metrics.positions_count
            }
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {}
    
    def calculate_performance_history(self, portfolio: Dict, trades: List[Trade]) -> List[Dict]:
        """Calculate portfolio performance over time"""
        performance_history = []
        
        # Group trades by date
        trades_by_date = {}
        for trade in trades:
            date_str = trade.date.strftime('%Y-%m-%d')
            if date_str not in trades_by_date:
                trades_by_date[date_str] = []
            trades_by_date[date_str].append(trade)
        
        # Calculate performance for each date
        current_portfolio = {
            'cash_balance': 100000,  # Initial capital
            'positions': {}
        }
        
        for date_str, daily_trades in sorted(trades_by_date.items()):
            for trade in daily_trades:
                current_portfolio = self.simulate_trade(current_portfolio, trade)
            
            metrics = self.calculate_portfolio_metrics(current_portfolio)
            
            performance_history.append({
                'date': date_str,
                'total_value': metrics.total_value,
                'total_pnl': metrics.total_pnl,
                'total_pnl_percent': metrics.total_pnl_percent,
                'positions_count': metrics.positions_count
            })
        
        return performance_history
    
    def create_portfolio(self, user_id: str, name: str, description: str = None) -> Dict:
        """Create a new portfolio"""
        try:
            portfolio_id = f"portfolio_{user_id}_{int(datetime.now().timestamp())}"
            
            portfolio_data = {
                'id': portfolio_id,
                'user_id': user_id,
                'name': name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'cash_balance': 0.0,
                'positions': {},
                'trades': []
            }
            
            # Save to database if Supabase is available
            if self.supabase:
                self.supabase.table('portfolios').insert(portfolio_data).execute()
            
            return portfolio_data
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            raise
    
    def get_user_portfolios(self, user_id: str) -> List[Dict]:
        """Get all portfolios for a user"""
        try:
            if self.supabase:
                response = self.supabase.table('portfolios').select('*').eq('user_id', user_id).execute()
                return response.data
            else:
                # Mock data for testing
                return [{
                    'id': f'portfolio_{user_id}_1',
                    'name': 'My Portfolio',
                    'description': 'Main investment portfolio',
                    'cash_balance': 50000.0,
                    'positions_count': 4
                }]
        except Exception as e:
            logger.error(f"Error getting user portfolios: {e}")
            return []
    
    def add_trade(self, portfolio_id: str, trade: Trade) -> Dict:
        """Add a trade to a portfolio"""
        try:
            # Get portfolio
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Add trade
            portfolio['trades'].append(trade)
            
            # Update portfolio
            portfolio = self.simulate_trade(portfolio, trade)
            
            # Save to database
            if self.supabase:
                self.supabase.table('portfolios').update(portfolio).eq('id', portfolio_id).execute()
            
            return portfolio
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            raise
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio by ID"""
        try:
            if self.supabase:
                response = self.supabase.table('portfolios').select('*').eq('id', portfolio_id).execute()
                return response.data[0] if response.data else None
            else:
                # Mock portfolio for testing
                return {
                    'id': portfolio_id,
                    'name': 'Test Portfolio',
                    'cash_balance': 50000.0,
                    'positions': {},
                    'trades': []
                }
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return None

# Initialize service
portfolio_service = PortfolioService() 