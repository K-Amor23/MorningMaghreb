#!/usr/bin/env python3
"""
Manual OHLCV Data Entry Script for Top 20 Moroccan Companies
Generates realistic 90-day price data and inserts into Supabase
"""

import json
import csv
import os
import sys
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("Supabase client not available, will only generate CSV files")

# Top 20 Moroccan companies with realistic base prices
TOP_20_COMPANIES = {
    'ATW': {
        'name': 'Attijariwafa Bank',
        'base_price': 155.97,
        'volatility': 0.025,
        'trend': 0.0002,
        'volume_base': 1500000
    },
    'IAM': {
        'name': 'Maroc Telecom',
        'base_price': 89.45,
        'volatility': 0.02,
        'trend': 0.0001,
        'volume_base': 800000
    },
    'BCP': {
        'name': 'Banque Centrale Populaire',
        'base_price': 245.60,
        'volatility': 0.03,
        'trend': 0.0003,
        'volume_base': 1200000
    },
    'BMCE': {
        'name': 'BMCE Bank of Africa',
        'base_price': 18.75,
        'volatility': 0.035,
        'trend': 0.0004,
        'volume_base': 2000000
    },
    'CIH': {
        'name': 'CIH Bank',
        'base_price': 12.30,
        'volatility': 0.04,
        'trend': 0.0005,
        'volume_base': 3000000
    },
    'CMT': {
        'name': 'Compagnie Minière de Touissit',
        'base_price': 45.20,
        'volatility': 0.045,
        'trend': 0.0006,
        'volume_base': 500000
    },
    'CTM': {
        'name': 'CTM',
        'base_price': 28.90,
        'volatility': 0.03,
        'trend': 0.0002,
        'volume_base': 400000
    },
    'DRI': {
        'name': 'Dari Couspate',
        'base_price': 35.60,
        'volatility': 0.035,
        'trend': 0.0003,
        'volume_base': 300000
    },
    'FEN': {
        'name': 'Fenosa',
        'base_price': 15.80,
        'volatility': 0.04,
        'trend': 0.0004,
        'volume_base': 600000
    },
    'IAM': {
        'name': 'Maroc Telecom',
        'base_price': 89.45,
        'volatility': 0.02,
        'trend': 0.0001,
        'volume_base': 800000
    },
    'JET': {
        'name': 'Jet Contractors',
        'base_price': 8.90,
        'volatility': 0.05,
        'trend': 0.0007,
        'volume_base': 1000000
    },
    'LES': {
        'name': 'Lesieur Cristal',
        'base_price': 42.30,
        'volatility': 0.025,
        'trend': 0.0002,
        'volume_base': 250000
    },
    'MNG': {
        'name': 'Managem',
        'base_price': 185.40,
        'volatility': 0.04,
        'trend': 0.0005,
        'volume_base': 400000
    },
    'MOR': {
        'name': 'Maroc Telecom',
        'base_price': 89.45,
        'volatility': 0.02,
        'trend': 0.0001,
        'volume_base': 800000
    },
    'SID': {
        'name': 'Sonasid',
        'base_price': 125.60,
        'volatility': 0.035,
        'trend': 0.0004,
        'volume_base': 350000
    },
    'SNP': {
        'name': 'Snep',
        'base_price': 22.80,
        'volatility': 0.03,
        'trend': 0.0003,
        'volume_base': 450000
    },
    'TMA': {
        'name': 'Taqa Morocco',
        'base_price': 12.45,
        'volatility': 0.04,
        'trend': 0.0005,
        'volume_base': 700000
    },
    'WAA': {
        'name': 'Wafa Assurance',
        'base_price': 18.90,
        'volatility': 0.035,
        'trend': 0.0003,
        'volume_base': 550000
    },
    'WAL': {
        'name': 'Wafa Assurance',
        'base_price': 18.90,
        'volatility': 0.035,
        'trend': 0.0003,
        'volume_base': 550000
    },
    'ZAL': {
        'name': 'Zellidja',
        'base_price': 65.30,
        'volatility': 0.04,
        'trend': 0.0004,
        'volume_base': 200000
    }
}

def generate_ohlcv_data(ticker: str, company_info: Dict[str, Any], days: int = 90) -> List[Dict[str, Any]]:
    """
    Generate realistic OHLCV data for a company
    """
    prices = []
    current_price = company_info['base_price']
    today = datetime.now()
    
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        
        # Generate realistic price movement
        volatility = company_info['volatility']
        trend = company_info['trend']
        random_change = (random.random() - 0.5) * volatility
        
        # Calculate new price
        previous_price = current_price
        current_price = previous_price * (1 + trend + random_change)
        
        # Generate OHLC
        open_price = previous_price * (1 + (random.random() - 0.5) * 0.01)
        close_price = current_price
        high_price = max(open_price, close_price) * (1 + random.random() * 0.005)
        low_price = min(open_price, close_price) * (1 - random.random() * 0.005)
        
        # Generate volume
        volume_base = company_info['volume_base']
        volume = int(volume_base * (0.8 + random.random() * 0.4))  # ±20% variation
        
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
    
    return prices

def save_to_csv(ticker: str, data: List[Dict[str, Any]], output_dir: str = 'data/ohlcv'):
    """
    Save OHLCV data to CSV file
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'{ticker}_ohlcv_90days.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'open', 'high', 'low', 'close', 'volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    
    print(f"✅ Saved {len(data)} records to {filename}")
    return filename

def insert_to_supabase(ticker: str, data: List[Dict[str, Any]], supabase_url: str = None, supabase_key: str = None):
    """
    Insert OHLCV data into Supabase
    """
    if not supabase_url or not supabase_key:
        print("⚠️  Supabase credentials not provided, skipping database insertion")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Prepare data for insertion
        records = []
        for row in data:
            records.append({
                'ticker': ticker,
                'date': row['date'],
                'open_price': row['open'],
                'high_price': row['high'],
                'low_price': row['low'],
                'close_price': row['close'],
                'volume': row['volume'],
                'created_at': datetime.now().isoformat()
            })
        
        # Insert data in batches
        batch_size = 50
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            result = supabase.table('company_prices').insert(batch).execute()
            
            if hasattr(result, 'error') and result.error:
                print(f"❌ Error inserting batch for {ticker}: {result.error}")
                return False
        
        print(f"✅ Successfully inserted {len(records)} records for {ticker} into Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting data for {ticker}: {str(e)}")
        return False

def create_supabase_table_sql():
    """
    Generate SQL for creating the company_prices table
    """
    return """
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
    """

def main():
    """
    Main function to generate and insert OHLCV data
    """
    print("🚀 Starting Manual OHLCV Data Generation for Top 20 Companies")
    print("=" * 60)
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    # Create output directory
    output_dir = 'data/ohlcv'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate data for each company
    all_data = {}
    csv_files = []
    
    for ticker, company_info in TOP_20_COMPANIES.items():
        print(f"\n📊 Generating data for {ticker} ({company_info['name']})...")
        
        # Generate OHLCV data
        ohlcv_data = generate_ohlcv_data(ticker, company_info)
        all_data[ticker] = ohlcv_data
        
        # Save to CSV
        csv_file = save_to_csv(ticker, ohlcv_data, output_dir)
        csv_files.append(csv_file)
        
        # Insert to Supabase if credentials are available
        if supabase_url and supabase_key:
            insert_to_supabase(ticker, ohlcv_data, supabase_url, supabase_key)
    
    # Create summary report
    summary_file = os.path.join(output_dir, 'generation_summary.json')
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_companies': len(TOP_20_COMPANIES),
        'days_per_company': 90,
        'total_records': len(TOP_20_COMPANIES) * 90,
        'companies': list(TOP_20_COMPANIES.keys()),
        'csv_files': csv_files,
        'supabase_inserted': bool(supabase_url and supabase_key)
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ OHLCV Data Generation Complete!")
    print(f"📁 CSV files saved to: {output_dir}")
    print(f"📊 Total records generated: {summary['total_records']}")
    print(f"🏢 Companies processed: {summary['total_companies']}")
    
    if supabase_url and supabase_key:
        print("🗄️  Data inserted into Supabase")
    else:
        print("⚠️  Supabase credentials not found - data only saved to CSV")
        print("   Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables to insert to database")
    
    print(f"📋 Summary saved to: {summary_file}")
    
    # Print SQL for table creation
    print("\n📝 SQL for creating company_prices table:")
    print("-" * 40)
    print(create_supabase_table_sql())

if __name__ == "__main__":
    main() 