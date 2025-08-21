"""
YFinance Wrapper for Casablanca Stock Exchange Data

This module provides a wrapper around yfinance for fetching Moroccan stock data
"""

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    """Stock data structure"""
    ticker: str
    name: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    scraped_at: datetime

class YFinanceWrapper:
    """Wrapper for yfinance to fetch Moroccan stock data"""
    
    def __init__(self):
        self.session = None
        
        # Moroccan stock tickers with .MA suffix for Yahoo Finance
        self.moroccan_tickers = [
            "ATW.MA", "IAM.MA", "BCP.MA", "BMCE.MA", "CIH.MA", 
            "WAA.MA", "SBM.MA", "NAKL.MA", "ZDJ.MA", "REB.MA",
            "BAL.MA", "AFI.MA", "LES.MA", "SRM.MA", "IBMC.MA", 
            "S2M.MA", "RIS.MA", "MIC.MA", "VICENNE.MA"
        ]
    
    def get_stock_info(self, ticker: str) -> Optional[StockData]:
        """Get stock information for a specific ticker"""
        try:
            logger.info(f"Fetching data for {ticker}...")
            
            # Create yfinance ticker object
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            
            # Get current market data
            hist = stock.history(period="1d")
            if hist.empty:
                logger.warning(f"No historical data for {ticker}")
                return None
            
            # Extract current day data
            current_data = hist.iloc[-1]
            
            # Create stock data object
            stock_data = StockData(
                ticker=ticker.replace('.MA', ''),
                name=info.get('longName', ticker),
                current_price=float(current_data['Close']),
                open_price=float(current_data['Open']),
                high_price=float(current_data['High']),
                low_price=float(current_data['Low']),
                volume=int(current_data['Volume']),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow'),
                scraped_at=datetime.now()
            )
            
            logger.info(f"✅ Successfully fetched data for {ticker}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_all_moroccan_stocks(self) -> List[StockData]:
        """Get data for all Moroccan stocks"""
        logger.info("Fetching data for all Moroccan stocks...")
        
        stocks = []
        
        for ticker in self.moroccan_tickers:
            try:
                stock_data = self.get_stock_info(ticker)
                if stock_data:
                    stocks.append(stock_data)
                
                # Add delay to be respectful
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                continue
        
        logger.info(f"✅ Fetched data for {len(stocks)} Moroccan stocks")
        return stocks
    
    def get_historical_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Get historical data for a ticker"""
        try:
            logger.info(f"Fetching historical data for {ticker} (period: {period})...")
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if not hist.empty:
                logger.info(f"✅ Successfully fetched {len(hist)} historical records for {ticker}")
                return hist
            else:
                logger.warning(f"No historical data for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None
    
    def get_dividend_history(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get dividend history for a ticker"""
        try:
            logger.info(f"Fetching dividend history for {ticker}...")
            
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            
            if not dividends.empty:
                logger.info(f"✅ Successfully fetched {len(dividends)} dividend records for {ticker}")
                return dividends
            else:
                logger.info(f"No dividend history for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching dividend history for {ticker}: {e}")
            return None
    
    def get_earnings_calendar(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get earnings calendar for a ticker"""
        try:
            logger.info(f"Fetching earnings calendar for {ticker}...")
            
            stock = yf.Ticker(ticker)
            earnings = stock.earnings
            
            if not earnings.empty:
                logger.info(f"✅ Successfully fetched {len(earnings)} earnings records for {ticker}")
                return earnings
            else:
                logger.info(f"No earnings data for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {ticker}: {e}")
            return None
    
    def export_stock_data(self, stocks: List[StockData], output_dir: str = "data/yfinance") -> str:
        """Export stock data to CSV file"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"moroccan_stocks_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame([vars(stock) for stock in stocks])
            df.to_csv(filepath, index=False)
            
            logger.info(f"Data exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise

def main():
    """Main function for testing"""
    wrapper = YFinanceWrapper()
    
    # Get all Moroccan stocks
    stocks = wrapper.get_all_moroccan_stocks()
    
    if stocks:
        # Export data
        output_dir = "data/yfinance"
        filepath = wrapper.export_stock_data(stocks, output_dir)
        print(f"✅ Data collection completed! Exported to {filepath}")
        print(f"   - Stocks: {len(stocks)}")
        
        # Show sample data
        for stock in stocks[:3]:
            print(f"   {stock.ticker}: {stock.name} - {stock.current_price} MAD")
    else:
        print("❌ No stock data was collected.")

if __name__ == "__main__":
    main()
