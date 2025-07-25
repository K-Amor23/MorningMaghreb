#!/usr/bin/env python3
"""
Insert OHLCV Data to Supabase

This script reads OHLCV CSV files and inserts them into the Supabase database.
It handles the companies table and company_prices table.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Load environment variables from .env file
def load_env():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env()

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available. Install with: pip install supabase-py")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OHLCVDataInserter:
    """Insert OHLCV data into Supabase"""
    
    def __init__(self):
        # Supabase client
        self.supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_service_key:
            logger.error("❌ Supabase credentials not found. Set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
            sys.exit(1)
        
        self.supabase = create_client(self.supabase_url, self.supabase_service_key)
        logger.info("✅ Supabase client initialized")
        
        # Data directories
        self.ohlcv_dir = Path("apps/backend/etl/data/ohlcv")
        self.companies_file = Path("apps/backend/data/cse_companies_african_markets.json")
        
        # Load companies data
        self.companies = self.load_companies()
    
    def load_companies(self) -> List[Dict]:
        """Load companies from African Markets data"""
        try:
            if not self.companies_file.exists():
                logger.error(f"❌ Companies file not found: {self.companies_file}")
                return []
            
            with open(self.companies_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            logger.info(f"✅ Loaded {len(companies_data)} companies from African Markets data")
            return companies_data
            
        except Exception as e:
            logger.error(f"❌ Error loading companies: {str(e)}")
            return []
    
    def insert_companies(self) -> bool:
        """Insert companies into the companies table"""
        try:
            logger.info("📊 Inserting companies into database...")
            
            # Prepare companies data
            companies_to_insert = []
            for company in self.companies:
                companies_to_insert.append({
                    'ticker': company['ticker'],
                    'name': company.get('name', ''),
                    'sector': company.get('sector', ''),
                    'industry': company.get('sector', ''),  # Using sector as industry for now
                    'market_cap_billion': company.get('market_cap_billion'),
                    'price': company.get('price'),
                    'change_1d_percent': company.get('change_1d_percent'),
                    'change_ytd_percent': company.get('change_ytd_percent'),
                    'size_category': company.get('size_category', 'Small Cap'),
                    'sector_group': company.get('sector_group', ''),
                    'exchange': company.get('exchange', 'Casablanca Stock Exchange (BVC)'),
                    'country': company.get('country', 'Morocco'),
                    'company_url': company.get('company_url'),
                    'is_active': True
                })
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(companies_to_insert), batch_size):
                batch = companies_to_insert[i:i + batch_size]
                
                result = self.supabase.table('companies').upsert(
                    batch,
                    on_conflict='ticker'
                ).execute()
                
                if hasattr(result, 'error') and result.error:
                    logger.error(f"❌ Error inserting companies batch: {result.error}")
                    return False
                
                logger.info(f"✅ Inserted companies batch {i//batch_size + 1}/{(len(companies_to_insert) + batch_size - 1) // batch_size}")
            
            logger.info(f"✅ Successfully inserted {len(companies_to_insert)} companies")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting companies: {str(e)}")
            return False
    
    def get_company_id(self, ticker: str) -> Optional[str]:
        """Get company ID from ticker"""
        try:
            result = self.supabase.table('companies').select('id').eq('ticker', ticker).execute()
            if result.data:
                return result.data[0]['id']
            return None
        except Exception as e:
            logger.error(f"❌ Error getting company ID for {ticker}: {str(e)}")
            return None
    
    def insert_ohlcv_data(self, csv_file: Path) -> bool:
        """Insert OHLCV data from a CSV file"""
        try:
            ticker = csv_file.stem  # Get ticker from filename (e.g., "ATW_ohlcv_90days.csv" -> "ATW")
            
            logger.info(f"📈 Processing OHLCV data for {ticker}")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Get company ID
            company_id = self.get_company_id(ticker)
            if not company_id:
                logger.warning(f"⚠️  Company {ticker} not found in database, skipping")
                return False
            
            # Prepare data for insertion
            prices_to_insert = []
            for _, row in df.iterrows():
                prices_to_insert.append({
                    'company_id': company_id,
                    'ticker': ticker,
                    'date': row['date'],
                    'open': row.get('open'),
                    'high': row.get('high'),
                    'low': row.get('low'),
                    'close': row.get('close'),
                    'volume': row.get('volume'),
                    'adjusted_close': row.get('adjusted_close', row.get('close'))
                })
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(prices_to_insert), batch_size):
                batch = prices_to_insert[i:i + batch_size]
                
                result = self.supabase.table('company_prices').upsert(
                    batch,
                    on_conflict='ticker,date'
                ).execute()
                
                if hasattr(result, 'error') and result.error:
                    logger.error(f"❌ Error inserting prices for {ticker}: {result.error}")
                    return False
            
            logger.info(f"✅ Successfully inserted {len(prices_to_insert)} price records for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {csv_file}: {str(e)}")
            return False
    
    def insert_all_ohlcv_data(self) -> bool:
        """Insert all OHLCV data from CSV files"""
        try:
            if not self.ohlcv_dir.exists():
                logger.error(f"❌ OHLCV directory not found: {self.ohlcv_dir}")
                return False
            
            # Find all CSV files
            csv_files = list(self.ohlcv_dir.glob("*_ohlcv_*.csv"))
            logger.info(f"📁 Found {len(csv_files)} OHLCV CSV files")
            
            if not csv_files:
                logger.warning("⚠️  No OHLCV CSV files found")
                return False
            
            # Process each file
            success_count = 0
            for csv_file in csv_files:
                if self.insert_ohlcv_data(csv_file):
                    success_count += 1
            
            logger.info(f"✅ Successfully processed {success_count}/{len(csv_files)} OHLCV files")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error processing OHLCV data: {str(e)}")
            return False
    
    def run(self) -> bool:
        """Run the complete insertion process"""
        logger.info("🚀 Starting OHLCV data insertion to Supabase")
        
        # Step 1: Insert companies
        if not self.insert_companies():
            logger.error("❌ Failed to insert companies")
            return False
        
        # Step 2: Insert OHLCV data
        if not self.insert_all_ohlcv_data():
            logger.error("❌ Failed to insert OHLCV data")
            return False
        
        logger.info("✅ OHLCV data insertion completed successfully")
        return True

def main():
    """Main function"""
    inserter = OHLCVDataInserter()
    success = inserter.run()
    
    if success:
        print("\n📋 INSERTION SUMMARY:")
        print("   ✅ Companies inserted successfully")
        print("   ✅ OHLCV data inserted successfully")
        print("   🎉 All data is now available in Supabase")
    else:
        print("\n❌ INSERTION FAILED")
        print("   Check the logs above for details")

if __name__ == "__main__":
    main() 