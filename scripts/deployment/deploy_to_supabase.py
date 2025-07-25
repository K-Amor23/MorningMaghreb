#!/usr/bin/env python3
"""
Supabase Deployment Script for Casablanca Insights
Deploys OHLCV data and syncs real data to Supabase
"""

import os
import sys
import json
import csv
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not available. Install with: pip install supabase")
    sys.exit(1)

class SupabaseDeployer:
    """Handles Supabase deployment and data synchronization"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Supabase credentials not found in environment variables")
            print("   Set SUPABASE_URL and SUPABASE_ANON_KEY")
            sys.exit(1)
        
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.service_client = create_client(self.supabase_url, self.supabase_service_key)
        
        print(f"✅ Connected to Supabase: {self.supabase_url}")
    
    def check_supabase_cli(self):
        """Check if Supabase CLI is installed"""
        try:
            result = subprocess.run(['supabase', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Supabase CLI: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Supabase CLI not found")
            print("   Install with: npm install -g supabase")
            return False
    
    def create_database_schema(self):
        """Create the database schema for OHLCV data"""
        schema_sql = """
        -- Create company_prices table for OHLCV data
        CREATE TABLE IF NOT EXISTS company_prices (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(10,2) NOT NULL,
            high_price DECIMAL(10,2) NOT NULL,
            low_price DECIMAL(10,2) NOT NULL,
            close_price DECIMAL(10,2) NOT NULL,
            volume INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
        CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
        CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date);

        -- Create unique constraint to prevent duplicates
        ALTER TABLE company_prices ADD CONSTRAINT unique_ticker_date UNIQUE (ticker, date);

        -- Create trigger to update updated_at timestamp
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        CREATE TRIGGER update_company_prices_updated_at 
            BEFORE UPDATE ON company_prices 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();

        -- Create companies table if it doesn't exist
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            sector VARCHAR(100),
            market_cap DECIMAL(20,2),
            current_price DECIMAL(10,2),
            price_change DECIMAL(10,2),
            price_change_percent DECIMAL(5,2),
            pe_ratio DECIMAL(10,2),
            dividend_yield DECIMAL(5,2),
            roe DECIMAL(5,2),
            shares_outstanding BIGINT,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create market_data table for aggregated data
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            data_type VARCHAR(50) NOT NULL, -- 'ohlcv', 'financials', 'news'
            data JSONB NOT NULL,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create indexes for market_data
        CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
        CREATE INDEX IF NOT EXISTS idx_market_data_type ON market_data(data_type);
        CREATE INDEX IF NOT EXISTS idx_market_data_ticker_type ON market_data(ticker, data_type);
        """
        
        try:
            # Execute schema creation
            result = self.service_client.rpc('exec_sql', {'sql': schema_sql}).execute()
            print("✅ Database schema created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating schema: {str(e)}")
            return False
    
    def load_ohlcv_data(self):
        """Load OHLCV data from CSV files and insert into Supabase"""
        ohlcv_dir = "apps/backend/etl/data/ohlcv"
        
        if not os.path.exists(ohlcv_dir):
            print(f"❌ OHLCV data directory not found: {ohlcv_dir}")
            return False
        
        csv_files = [f for f in os.listdir(ohlcv_dir) if f.endswith('_ohlcv_90days.csv')]
        
        if not csv_files:
            print(f"❌ No OHLCV CSV files found in {ohlcv_dir}")
            return False
        
        total_records = 0
        successful_companies = 0
        
        for csv_file in csv_files:
            ticker = csv_file.split('_')[0]
            file_path = os.path.join(ohlcv_dir, csv_file)
            
            print(f"📊 Processing {ticker}...")
            
            try:
                # Read CSV file
                records = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append({
                            'ticker': ticker,
                            'date': row['date'],
                            'open_price': float(row['open']),
                            'high_price': float(row['high']),
                            'low_price': float(row['low']),
                            'close_price': float(row['close']),
                            'volume': int(row['volume']),
                            'created_at': datetime.now().isoformat()
                        })
                
                # Insert data in batches
                batch_size = 50
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    # Use upsert to handle duplicates
                    result = self.service_client.table('company_prices').upsert(
                        batch, 
                        on_conflict='ticker,date'
                    ).execute()
                    
                    if hasattr(result, 'error') and result.error:
                        print(f"❌ Error inserting batch for {ticker}: {result.error}")
                        continue
                
                total_records += len(records)
                successful_companies += 1
                print(f"✅ {ticker}: {len(records)} records inserted")
                
            except Exception as e:
                print(f"❌ Error processing {ticker}: {str(e)}")
        
        print(f"\n📊 OHLCV Data Summary:")
        print(f"   Companies processed: {successful_companies}/{len(csv_files)}")
        print(f"   Total records: {total_records}")
        
        return successful_companies > 0
    
    def sync_company_data(self):
        """Sync company metadata from African Markets data"""
        try:
            # Load African Markets data
            african_markets_file = "apps/backend/data/cse_companies_african_markets.json"
            
            if not os.path.exists(african_markets_file):
                print(f"❌ African Markets data not found: {african_markets_file}")
                return False
            
            with open(african_markets_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            # Prepare company records
            company_records = []
            for company in companies_data:
                if company.get('ticker'):
                    company_records.append({
                        'ticker': company['ticker'].upper(),
                        'name': company.get('name') or company.get('company_name', ''),
                        'sector': company.get('sector', ''),
                        'market_cap': company.get('market_cap_billion', 0) * 1000000000 if company.get('market_cap_billion') else None,
                        'pe_ratio': company.get('pe_ratio'),
                        'dividend_yield': company.get('dividend_yield'),
                        'roe': company.get('roe'),
                        'shares_outstanding': company.get('shares_outstanding'),
                        'last_updated': datetime.now().isoformat()
                    })
            
            # Insert company data
            result = self.service_client.table('companies').upsert(
                company_records,
                on_conflict='ticker'
            ).execute()
            
            if hasattr(result, 'error') and result.error:
                print(f"❌ Error syncing company data: {result.error}")
                return False
            
            print(f"✅ Company data synced: {len(company_records)} companies")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing company data: {str(e)}")
            return False
    
    def create_api_endpoints(self):
        """Create database functions for API endpoints"""
        functions_sql = """
        -- Function to get company summary with latest price
        CREATE OR REPLACE FUNCTION get_company_summary(ticker_param VARCHAR)
        RETURNS JSON AS $$
        DECLARE
            company_data JSON;
            price_data JSON;
            latest_price RECORD;
        BEGIN
            -- Get company data
            SELECT to_json(c.*) INTO company_data
            FROM companies c
            WHERE c.ticker = ticker_param;
            
            -- Get latest price data
            SELECT cp.* INTO latest_price
            FROM company_prices cp
            WHERE cp.ticker = ticker_param
            ORDER BY cp.date DESC
            LIMIT 1;
            
            -- Get 90 days of price data
            SELECT json_agg(
                json_build_object(
                    'date', cp.date,
                    'open', cp.open_price,
                    'high', cp.high_price,
                    'low', cp.low_price,
                    'close', cp.close_price,
                    'volume', cp.volume
                )
            ) INTO price_data
            FROM company_prices cp
            WHERE cp.ticker = ticker_param
            ORDER BY cp.date DESC
            LIMIT 90;
            
            -- Return combined data
            RETURN json_build_object(
                'company', company_data,
                'priceData', json_build_object(
                    'last90Days', price_data,
                    'currentPrice', latest_price.close_price,
                    'priceChange', latest_price.close_price - (
                        SELECT cp2.close_price 
                        FROM company_prices cp2 
                        WHERE cp2.ticker = ticker_param 
                        ORDER BY cp2.date DESC 
                        LIMIT 1 OFFSET 1
                    ),
                    'priceChangePercent', (
                        (latest_price.close_price - (
                            SELECT cp2.close_price 
                            FROM company_prices cp2 
                            WHERE cp2.ticker = ticker_param 
                            ORDER BY cp2.date DESC 
                            LIMIT 1 OFFSET 1
                        )) / (
                            SELECT cp2.close_price 
                            FROM company_prices cp2 
                            WHERE cp2.ticker = ticker_param 
                            ORDER BY cp2.date DESC 
                            LIMIT 1 OFFSET 1
                        ) * 100
                    )
                ),
                'metadata', json_build_object(
                    'dataQuality', 'real',
                    'lastUpdated', latest_price.updated_at,
                    'sources', json_build_array('Supabase Database')
                )
            );
        END;
        $$ LANGUAGE plpgsql;

        -- Function to get all companies with latest prices
        CREATE OR REPLACE FUNCTION get_all_companies()
        RETURNS JSON AS $$
        DECLARE
            companies_data JSON;
        BEGIN
            SELECT json_agg(
                json_build_object(
                    'ticker', c.ticker,
                    'name', c.name,
                    'sector', c.sector,
                    'currentPrice', cp.close_price,
                    'priceChange', cp.close_price - cp2.close_price,
                    'priceChangePercent', ((cp.close_price - cp2.close_price) / cp2.close_price * 100),
                    'marketCap', c.market_cap,
                    'volume', cp.volume
                )
            ) INTO companies_data
            FROM companies c
            LEFT JOIN LATERAL (
                SELECT cp.*
                FROM company_prices cp
                WHERE cp.ticker = c.ticker
                ORDER BY cp.date DESC
                LIMIT 1
            ) cp ON true
            LEFT JOIN LATERAL (
                SELECT cp2.*
                FROM company_prices cp2
                WHERE cp2.ticker = c.ticker
                ORDER BY cp2.date DESC
                LIMIT 1 OFFSET 1
            ) cp2 ON true;
            
            RETURN companies_data;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        try:
            result = self.service_client.rpc('exec_sql', {'sql': functions_sql}).execute()
            print("✅ API functions created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating API functions: {str(e)}")
            return False
    
    def test_deployment(self):
        """Test the deployment by querying the data"""
        try:
            # Test company data
            result = self.client.table('companies').select('*').limit(5).execute()
            print(f"✅ Company data test: {len(result.data)} companies found")
            
            # Test OHLCV data
            result = self.client.table('company_prices').select('*').limit(5).execute()
            print(f"✅ OHLCV data test: {len(result.data)} price records found")
            
            # Test API function
            result = self.client.rpc('get_company_summary', {'ticker_param': 'ATW'}).execute()
            if result.data:
                print("✅ API function test: Company summary retrieved successfully")
            else:
                print("⚠️  API function test: No data returned")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment test failed: {str(e)}")
            return False
    
    def deploy(self):
        """Main deployment process"""
        print("🚀 Starting Supabase Deployment")
        print("=" * 60)
        
        # Check Supabase CLI
        if not self.check_supabase_cli():
            print("⚠️  Continuing without Supabase CLI...")
        
        # Create database schema
        print("\n📊 Creating database schema...")
        if not self.create_database_schema():
            print("❌ Schema creation failed")
            return False
        
        # Sync company data
        print("\n🏢 Syncing company data...")
        if not self.sync_company_data():
            print("❌ Company data sync failed")
            return False
        
        # Load OHLCV data
        print("\n📈 Loading OHLCV data...")
        if not self.load_ohlcv_data():
            print("❌ OHLCV data loading failed")
            return False
        
        # Create API functions
        print("\n🔧 Creating API functions...")
        if not self.create_api_endpoints():
            print("❌ API functions creation failed")
            return False
        
        # Test deployment
        print("\n🧪 Testing deployment...")
        if not self.test_deployment():
            print("❌ Deployment test failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Supabase Deployment Complete!")
        print("=" * 60)
        print(f"🌐 Supabase URL: {self.supabase_url}")
        print("📊 Database schema created")
        print("🏢 Company data synced")
        print("📈 OHLCV data loaded")
        print("🔧 API functions created")
        print("\n🎯 Next steps:")
        print("   1. Update frontend to use Supabase API")
        print("   2. Test all endpoints with real data")
        print("   3. Deploy to production")
        
        return True

def main():
    """Main function"""
    deployer = SupabaseDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n🎉 Deployment successful! Your data is now live on Supabase.")
    else:
        print("\n❌ Deployment failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 