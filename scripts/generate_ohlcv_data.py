#!/usr/bin/env python3
"""
Generate Manual OHLCV Data for Top 20 Companies

This script generates realistic OHLCV data for the top 20 Moroccan companies
and saves them as CSV files for insertion into Supabase.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OHLCVDataGenerator:
    """Generate realistic OHLCV data for companies"""
    
    def __init__(self):
        self.output_dir = Path("apps/backend/etl/data/ohlcv")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load companies data
        self.companies = self.load_companies()
        
        # Top 20 companies by market cap (with correct ticker names)
        self.top_20_companies = [
            'ATW', 'IAM', 'BCP', 'GAZ', 'MNG', 'CIH', 'BOA', 'ADI', 'SID', 'TMA',
            'WAA', 'LES', 'CTM', 'CMT', 'SNP', 'JET', 'DARI', 'FBR', 'HPS', 'NEJ'
        ]
    
    def load_companies(self) -> List[Dict]:
        """Load companies from African Markets data"""
        try:
            companies_file = Path("apps/backend/data/cse_companies_african_markets.json")
            
            if not companies_file.exists():
                logger.error(f"Companies file not found: {companies_file}")
                return []
            
            with open(companies_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            logger.info(f"✅ Loaded {len(companies_data)} companies")
            return companies_data
            
        except Exception as e:
            logger.error(f"❌ Error loading companies: {str(e)}")
            return []
    
    def get_company_info(self, ticker: str) -> Dict:
        """Get company information by ticker"""
        for company in self.companies:
            if company.get('ticker') == ticker:
                return company
        return {}
    
    def generate_realistic_price_data(self, base_price: float, days: int = 90) -> List[Dict]:
        """Generate realistic OHLCV data"""
        prices = []
        current_price = base_price
        today = datetime.now()
        
        # Market parameters
        volatility = 0.02  # 2% daily volatility
        trend = 0.0001     # Slight upward trend
        volume_base = 1000000  # Base volume
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            
            # Generate price movement
            random_change = np.random.normal(0, volatility)
            trend_change = trend
            
            # Calculate new price
            new_price = current_price * (1 + trend_change + random_change)
            
            # Generate OHLC
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            close_price = new_price
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.003)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.003)))
            
            # Generate volume (correlated with price movement)
            volume_multiplier = 1 + abs(random_change) * 10  # Higher volume on big moves
            volume = int(volume_base * volume_multiplier * (0.8 + np.random.random() * 0.4))
            
            prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            current_price = close_price
        
        return prices
    
    def generate_company_ohlcv(self, ticker: str) -> bool:
        """Generate OHLCV data for a specific company"""
        try:
            company_info = self.get_company_info(ticker)
            
            if not company_info:
                logger.warning(f"⚠️  Company info not found for {ticker}")
                return False
            
            # Calculate base price from market cap
            market_cap = company_info.get('market_cap_billion', 1)
            base_price = market_cap * 100  # Simplified calculation
            
            # Generate price data
            price_data = self.generate_realistic_price_data(base_price)
            
            # Create DataFrame
            df = pd.DataFrame(price_data)
            
            # Save to CSV
            csv_file = self.output_dir / f"{ticker}_ohlcv_90days.csv"
            df.to_csv(csv_file, index=False)
            
            logger.info(f"✅ Generated OHLCV data for {ticker}: {len(price_data)} records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating data for {ticker}: {str(e)}")
            return False
    
    def generate_all_top_20(self) -> bool:
        """Generate OHLCV data for all top 20 companies"""
        logger.info("🚀 Generating OHLCV data for top 20 companies")
        
        success_count = 0
        for ticker in self.top_20_companies:
            if self.generate_company_ohlcv(ticker):
                success_count += 1
        
        logger.info(f"✅ Successfully generated data for {success_count}/{len(self.top_20_companies)} companies")
        return success_count == len(self.top_20_companies)
    
    def validate_generated_data(self) -> bool:
        """Validate the generated CSV files"""
        logger.info("🔍 Validating generated data...")
        
        for ticker in self.top_20_companies:
            csv_file = self.output_dir / f"{ticker}_ohlcv_90days.csv"
            
            if not csv_file.exists():
                logger.error(f"❌ CSV file not found: {csv_file}")
                return False
            
            try:
                df = pd.read_csv(csv_file)
                
                # Check required columns
                required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    logger.error(f"❌ Missing columns in {ticker}")
                    return False
                
                # Check data length
                if len(df) != 90:
                    logger.error(f"❌ Expected 90 days, got {len(df)} for {ticker}")
                    return False
                
                # Check data types
                if not all(df[col].dtype in ['float64', 'int64'] for col in ['open', 'high', 'low', 'close', 'volume']):
                    logger.error(f"❌ Invalid data types in {ticker}")
                    return False
                
                logger.info(f"✅ {ticker}: {len(df)} records, {df.columns.tolist()}")
                
            except Exception as e:
                logger.error(f"❌ Error validating {ticker}: {str(e)}")
                return False
        
        logger.info("✅ All generated data validated successfully")
        return True

def main():
    """Main function"""
    generator = OHLCVDataGenerator()
    
    # Generate data for top 20 companies
    if not generator.generate_all_top_20():
        logger.error("❌ Failed to generate data for all companies")
        return False
    
    # Validate generated data
    if not generator.validate_generated_data():
        logger.error("❌ Data validation failed")
        return False
    
    logger.info("🎉 OHLCV data generation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 