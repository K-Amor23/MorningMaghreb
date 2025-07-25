#!/usr/bin/env python3
"""
Advanced Analytics Service

This service computes technical indicators for each company daily:
- 10-day and 30-day moving averages
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume indicators

Features:
- Daily computation for all companies
- Batch processing for efficiency
- Supabase integration
- Error handling and logging
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
import time

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
        logging.FileHandler('analytics_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for computing technical indicators"""
    
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
        
        # Technical indicator parameters
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bollinger_period = 20
        self.bollinger_std = 2
        
        logger.info("✅ Analytics Service initialized")
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period).mean()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = self.calculate_ema(prices, self.macd_fast)
        ema_slow = self.calculate_ema(prices, self.macd_slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, self.macd_signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(prices, self.bollinger_period)
        std = prices.rolling(window=self.bollinger_period).std()
        upper_band = sma + (std * self.bollinger_std)
        lower_band = sma - (std * self.bollinger_std)
        return upper_band, sma, lower_band
    
    def calculate_volume_indicators(self, prices: pd.Series, volumes: pd.Series) -> Dict[str, pd.Series]:
        """Calculate volume-based indicators"""
        # Volume SMA
        volume_sma = self.calculate_sma(volumes, 20)
        
        # Price-Volume Trend
        pvt = (prices.pct_change() * volumes).cumsum()
        
        # On-Balance Volume (OBV)
        obv = pd.Series(index=prices.index, dtype=float)
        obv.iloc[0] = volumes.iloc[0]
        
        for i in range(1, len(prices)):
            if prices.iloc[i] > prices.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volumes.iloc[i]
            elif prices.iloc[i] < prices.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volumes.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return {
            'volume_sma': volume_sma,
            'pvt': pvt,
            'obv': obv
        }
    
    def generate_signals(self, prices: pd.Series, rsi: pd.Series, macd_line: pd.Series, 
                        signal_line: pd.Series, upper_band: pd.Series, lower_band: pd.Series) -> pd.Series:
        """Generate trading signals based on technical indicators"""
        signals = pd.Series(index=prices.index, data='hold')
        
        # RSI signals
        signals[rsi > 70] = 'sell'
        signals[rsi < 30] = 'buy'
        
        # MACD signals
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 'buy'
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = 'sell'
        
        # Bollinger Bands signals
        signals[prices > upper_band] = 'sell'
        signals[prices < lower_band] = 'buy'
        
        return signals
    
    def get_company_price_data(self, ticker: str, days: int = 60) -> Optional[pd.DataFrame]:
        """Get price data for a company"""
        try:
            if not self.supabase:
                logger.warning("⚠️  Supabase not configured")
                return None
            
            # Get price data from the last N days
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            result = self.supabase.table('company_prices').select('*').eq('ticker', ticker).gte('date', cutoff_date.isoformat()).order('date', ascending=True).execute()
            
            if not result.data:
                logger.warning(f"⚠️  No price data found for {ticker}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(result.data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Ensure we have enough data
            if len(df) < 30:
                logger.warning(f"⚠️  Insufficient data for {ticker}: {len(df)} records")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting price data for {ticker}: {str(e)}")
            return None
    
    def compute_indicators_for_company(self, ticker: str) -> Optional[Dict]:
        """Compute all technical indicators for a company"""
        try:
            logger.info(f"📊 Computing indicators for {ticker}")
            
            # Get price data
            df = self.get_company_price_data(ticker)
            if df is None:
                return None
            
            # Calculate indicators
            prices = df['close']
            volumes = df['volume']
            
            # Moving averages
            sma_10 = self.calculate_sma(prices, 10)
            sma_30 = self.calculate_sma(prices, 30)
            ema_12 = self.calculate_ema(prices, 12)
            ema_26 = self.calculate_ema(prices, 26)
            
            # RSI
            rsi = self.calculate_rsi(prices, self.rsi_period)
            
            # MACD
            macd_line, signal_line, histogram = self.calculate_macd(prices)
            
            # Bollinger Bands
            upper_band, middle_band, lower_band = self.calculate_bollinger_bands(prices)
            
            # Volume indicators
            volume_indicators = self.calculate_volume_indicators(prices, volumes)
            
            # Generate signals
            signals = self.generate_signals(prices, rsi, macd_line, signal_line, upper_band, lower_band)
            
            # Get latest values
            latest_idx = -1
            
            indicators = {
                'ticker': ticker,
                'date': df.iloc[latest_idx]['date'].date().isoformat(),
                'close_price': float(prices.iloc[latest_idx]),
                'volume': int(volumes.iloc[latest_idx]),
                
                # Moving averages
                'sma_10': float(sma_10.iloc[latest_idx]) if not pd.isna(sma_10.iloc[latest_idx]) else None,
                'sma_30': float(sma_30.iloc[latest_idx]) if not pd.isna(sma_30.iloc[latest_idx]) else None,
                'ema_12': float(ema_12.iloc[latest_idx]) if not pd.isna(ema_12.iloc[latest_idx]) else None,
                'ema_26': float(ema_26.iloc[latest_idx]) if not pd.isna(ema_26.iloc[latest_idx]) else None,
                
                # RSI
                'rsi': float(rsi.iloc[latest_idx]) if not pd.isna(rsi.iloc[latest_idx]) else None,
                
                # MACD
                'macd_line': float(macd_line.iloc[latest_idx]) if not pd.isna(macd_line.iloc[latest_idx]) else None,
                'macd_signal': float(signal_line.iloc[latest_idx]) if not pd.isna(signal_line.iloc[latest_idx]) else None,
                'macd_histogram': float(histogram.iloc[latest_idx]) if not pd.isna(histogram.iloc[latest_idx]) else None,
                
                # Bollinger Bands
                'bb_upper': float(upper_band.iloc[latest_idx]) if not pd.isna(upper_band.iloc[latest_idx]) else None,
                'bb_middle': float(middle_band.iloc[latest_idx]) if not pd.isna(middle_band.iloc[latest_idx]) else None,
                'bb_lower': float(lower_band.iloc[latest_idx]) if not pd.isna(lower_band.iloc[latest_idx]) else None,
                
                # Volume indicators
                'volume_sma': float(volume_indicators['volume_sma'].iloc[latest_idx]) if not pd.isna(volume_indicators['volume_sma'].iloc[latest_idx]) else None,
                'pvt': float(volume_indicators['pvt'].iloc[latest_idx]) if not pd.isna(volume_indicators['pvt'].iloc[latest_idx]) else None,
                'obv': float(volume_indicators['obv'].iloc[latest_idx]) if not pd.isna(volume_indicators['obv'].iloc[latest_idx]) else None,
                
                # Signals
                'signal': signals.iloc[latest_idx],
                'signal_strength': self.calculate_signal_strength(rsi.iloc[latest_idx], macd_line.iloc[latest_idx], signal_line.iloc[latest_idx], prices.iloc[latest_idx], upper_band.iloc[latest_idx], lower_band.iloc[latest_idx]),
                
                # Metadata
                'computed_at': datetime.now().isoformat(),
                'data_points': len(df)
            }
            
            logger.info(f"✅ Computed indicators for {ticker}")
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Error computing indicators for {ticker}: {str(e)}")
            return None
    
    def calculate_signal_strength(self, rsi: float, macd_line: float, signal_line: float, 
                                 price: float, upper_band: float, lower_band: float) -> float:
        """Calculate signal strength (0-100)"""
        strength = 50  # Neutral starting point
        
        # RSI contribution
        if rsi is not None:
            if rsi > 70:
                strength -= 20  # Strong sell
            elif rsi > 60:
                strength -= 10  # Weak sell
            elif rsi < 30:
                strength += 20  # Strong buy
            elif rsi < 40:
                strength += 10  # Weak buy
        
        # MACD contribution
        if macd_line is not None and signal_line is not None:
            if macd_line > signal_line:
                strength += 15  # Bullish
            else:
                strength -= 15  # Bearish
        
        # Bollinger Bands contribution
        if upper_band is not None and lower_band is not None:
            if price > upper_band:
                strength -= 15  # Overbought
            elif price < lower_band:
                strength += 15  # Oversold
        
        return max(0, min(100, strength))  # Clamp between 0-100
    
    def insert_analytics_to_supabase(self, indicators: Dict) -> bool:
        """Insert analytics data to Supabase"""
        try:
            if not self.supabase:
                return False
            
            # Insert into analytics_signals table
            result = self.supabase.table('analytics_signals').upsert(
                indicators,
                on_conflict='ticker,date'
            ).execute()
            
            logger.info(f"✅ Inserted analytics for {indicators['ticker']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting analytics for {indicators['ticker']}: {str(e)}")
            return False
    
    def get_companies_with_price_data(self) -> List[str]:
        """Get list of companies with recent price data"""
        try:
            if not self.supabase:
                return []
            
            # Get companies with price data in the last 30 days
            cutoff_date = (datetime.now() - timedelta(days=30)).date()
            
            result = self.supabase.table('company_prices').select('ticker').gte('date', cutoff_date.isoformat()).execute()
            
            if not result.data:
                return []
            
            # Get unique tickers
            tickers = list(set([item['ticker'] for item in result.data]))
            return tickers
            
        except Exception as e:
            logger.error(f"❌ Error getting companies with price data: {str(e)}")
            return []
    
    def run_daily_analytics(self) -> Dict:
        """Run daily analytics computation for all companies"""
        start_time = time.time()
        
        logger.info("🚀 Starting daily analytics computation...")
        
        # Get companies with price data
        companies = self.get_companies_with_price_data()
        logger.info(f"📊 Found {len(companies)} companies with price data")
        
        results = {
            'total_companies': len(companies),
            'processed': 0,
            'failed': 0,
            'successful': 0,
            'errors': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': 0
        }
        
        for i, ticker in enumerate(companies):
            try:
                logger.info(f"📈 Processing {i+1}/{len(companies)}: {ticker}")
                
                # Compute indicators
                indicators = self.compute_indicators_for_company(ticker)
                
                if indicators:
                    # Insert to Supabase
                    success = self.insert_analytics_to_supabase(indicators)
                    
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to insert analytics for {ticker}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"No indicators computed for {ticker}")
                
                results['processed'] += 1
                
                # Small delay to avoid overwhelming the database
                time.sleep(0.1)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing {ticker}: {str(e)}")
                logger.error(f"❌ Error processing {ticker}: {str(e)}")
        
        # Calculate completion time
        end_time = time.time()
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = end_time - start_time
        
        logger.info("✅ Daily analytics computation completed")
        logger.info(f"📊 Results: {results['successful']} successful, {results['failed']} failed")
        logger.info(f"⏱️  Duration: {results['duration']:.2f} seconds")
        
        return results

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Analytics Service')
    parser.add_argument('--ticker', type=str, help='Process specific ticker only')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    service = AnalyticsService()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Testing configuration...")
        companies = service.get_companies_with_price_data()
        print(f"   Companies with price data: {len(companies)}")
        print(f"   Sample companies: {companies[:5]}")
        return
    
    if args.ticker:
        # Process specific ticker
        print(f"📊 Processing specific ticker: {args.ticker}")
        indicators = service.compute_indicators_for_company(args.ticker)
        if indicators:
            print(f"✅ Indicators computed for {args.ticker}")
            print(json.dumps(indicators, indent=2))
        else:
            print(f"❌ Failed to compute indicators for {args.ticker}")
    else:
        # Run daily analytics for all companies
        print("🚀 Running daily analytics for all companies...")
        results = service.run_daily_analytics()
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 