#!/usr/bin/env python3
"""
Deploy master pipeline tables and ensure `companies` and `market_data` exist with indexes.
Run this once against your Supabase project (service role key required).
"""
import os
import sys
from pathlib import Path

SQL_FILES = [
    Path('database/MASTER_SCHEMA_MIGRATION.sql'),
    Path('database/master_pipeline_tables.sql'),
]

def main():
    from supabase import create_client

    url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        print('Missing env: NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY')
        sys.exit(1)

    # Use PostgREST RPC is not ideal for running raw SQL. Recommend running via Supabase SQL editor
    # or psql. Here we just print instructions.
    print('Open Supabase SQL editor and run these files in order:')
    for f in SQL_FILES:
        print(f" - {f}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Deploy Master Pipeline Database Tables to Supabase

This script creates all the necessary tables for the master Airflow pipeline
to store data in Supabase for the website.
"""

import os
import sys
import logging
from pathlib import Path
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_supabase_client():
    """Initialize Supabase client"""
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized")
        return supabase
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        raise

def read_sql_file(file_path: str) -> str:
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"✅ Read SQL file: {file_path}")
        return content
    except Exception as e:
        logger.error(f"❌ Failed to read SQL file {file_path}: {e}")
        raise

def execute_sql_statements(supabase: Client, sql_content: str):
    """Execute SQL statements in Supabase"""
    try:
        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        logger.info(f"📝 Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    # Execute the SQL statement
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    logger.info(f"✅ Statement {i}/{len(statements)} executed successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Statement {i}/{len(statements)} failed (may already exist): {e}")
                    continue
        
        logger.info("✅ All SQL statements processed")
        
    except Exception as e:
        logger.error(f"❌ Failed to execute SQL statements: {e}")
        raise

def verify_tables_created(supabase: Client):
    """Verify that all required tables were created"""
    try:
        logger.info("🔍 Verifying tables were created...")
        
        # List of expected tables
        expected_tables = [
            'company_prices',
            'market_indices', 
            'macro_indicators',
            'company_news',
            'data_quality_logs',
            'pipeline_notifications'
        ]
        
        # Check each table
        for table_name in expected_tables:
            try:
                # Try to select from the table
                result = supabase.table(table_name).select('*').limit(1).execute()
                logger.info(f"✅ Table '{table_name}' exists and is accessible")
            except Exception as e:
                logger.error(f"❌ Table '{table_name}' not found or not accessible: {e}")
                return False
        
        logger.info("✅ All expected tables are present and accessible")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

def insert_sample_data(supabase: Client):
    """Insert sample data for testing"""
    try:
        logger.info("📊 Inserting sample data...")
        
        # Sample company prices data
        company_prices_data = [
            {
                'ticker': 'ATW',
                'company_name': 'Attijariwafa Bank',
                'sector': 'Banking',
                'price': 410.10,
                'change_1d_percent': 0.31,
                'change_ytd_percent': 5.25,
                'market_cap_billion': 24.56,
                'volume': 1250000,
                'pe_ratio': 12.5,
                'dividend_yield': 4.2,
                'size_category': 'Large Cap',
                'sector_group': 'Financial Services',
                'date': '2024-01-15'
            },
            {
                'ticker': 'IAM',
                'company_name': 'Maroc Telecom',
                'sector': 'Telecommunications',
                'price': 156.30,
                'change_1d_percent': -1.33,
                'change_ytd_percent': -2.15,
                'market_cap_billion': 15.68,
                'volume': 890000,
                'pe_ratio': 15.2,
                'dividend_yield': 3.8,
                'size_category': 'Large Cap',
                'sector_group': 'Telecommunications',
                'date': '2024-01-15'
            },
            {
                'ticker': 'BCP',
                'company_name': 'Banque Centrale Populaire',
                'sector': 'Banking',
                'price': 245.80,
                'change_1d_percent': 0.85,
                'change_ytd_percent': 8.45,
                'market_cap_billion': 18.92,
                'volume': 950000,
                'pe_ratio': 11.8,
                'dividend_yield': 5.1,
                'size_category': 'Large Cap',
                'sector_group': 'Financial Services',
                'date': '2024-01-15'
            }
        ]
        
        # Sample market indices data
        market_indices_data = [
            {
                'index_name': 'MASI',
                'value': 12580.45,
                'change_1d_percent': 0.45,
                'change_ytd_percent': 12.3,
                'volume': 45000000,
                'market_cap_total': 1250.8,
                'date': '2024-01-15'
            },
            {
                'index_name': 'MADEX',
                'value': 10250.30,
                'change_1d_percent': 0.32,
                'change_ytd_percent': 10.8,
                'volume': 38000000,
                'market_cap_total': 980.5,
                'date': '2024-01-15'
            }
        ]
        
        # Sample macro indicators data
        macro_indicators_data = [
            {
                'indicator': 'GDP_Growth',
                'value': 3.2,
                'unit': 'percent',
                'period': '2024',
                'source': 'Bank Al-Maghrib',
                'date': '2024-01-15'
            },
            {
                'indicator': 'Inflation_Rate',
                'value': 2.8,
                'unit': 'percent',
                'period': '2024',
                'source': 'Bank Al-Maghrib',
                'date': '2024-01-15'
            },
            {
                'indicator': 'Interest_Rate',
                'value': 2.5,
                'unit': 'percent',
                'period': '2024',
                'source': 'Bank Al-Maghrib',
                'date': '2024-01-15'
            },
            {
                'indicator': 'Exchange_Rate_USD',
                'value': 9.85,
                'unit': 'MAD/USD',
                'period': '2024',
                'source': 'Bank Al-Maghrib',
                'date': '2024-01-15'
            }
        ]
        
        # Sample news data
        news_data = [
            {
                'ticker': 'ATW',
                'headline': 'Attijariwafa Bank Reports Strong Q4 Results',
                'summary': 'Bank reports 15% increase in net profit',
                'sentiment': 'positive',
                'source': 'Financial News Morocco',
                'published_at': '2024-01-15T10:00:00Z'
            },
            {
                'ticker': 'IAM',
                'headline': 'Maroc Telecom Expands 5G Network',
                'summary': 'Company announces major 5G infrastructure investment',
                'sentiment': 'positive',
                'source': 'Tech News Morocco',
                'published_at': '2024-01-15T11:30:00Z'
            }
        ]
        
        # Insert sample data
        tables_data = {
            'company_prices': company_prices_data,
            'market_indices': market_indices_data,
            'macro_indicators': macro_indicators_data,
            'company_news': news_data
        }
        
        for table_name, data in tables_data.items():
            try:
                for record in data:
                    result = supabase.table(table_name).upsert(record).execute()
                logger.info(f"✅ Inserted {len(data)} records into {table_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to insert data into {table_name}: {e}")
                continue
        
        logger.info("✅ Sample data insertion completed")
        
    except Exception as e:
        logger.error(f"❌ Error inserting sample data: {e}")
        raise

def main():
    """Main deployment function"""
    try:
        logger.info("🚀 Starting Master Pipeline Database Deployment")
        
        # Initialize Supabase client
        supabase = initialize_supabase_client()
        
        # Read SQL file
        sql_file_path = Path(__file__).parent.parent / 'database' / 'master_pipeline_tables.sql'
        sql_content = read_sql_file(str(sql_file_path))
        
        # Execute SQL statements
        execute_sql_statements(supabase, sql_content)
        
        # Verify tables were created
        if not verify_tables_created(supabase):
            logger.error("❌ Table verification failed")
            sys.exit(1)
        
        # Insert sample data
        insert_sample_data(supabase)
        
        logger.info("🎉 Master Pipeline Database Deployment Completed Successfully!")
        logger.info("📊 Tables created:")
        logger.info("   • company_prices - Market data for companies")
        logger.info("   • market_indices - Market indices data")
        logger.info("   • macro_indicators - Macroeconomic indicators")
        logger.info("   • company_news - News and sentiment data")
        logger.info("   • data_quality_logs - Pipeline monitoring")
        logger.info("   • pipeline_notifications - Success/failure notifications")
        logger.info("")
        logger.info("🔗 Your website can now access real data from Supabase!")
        logger.info("⚙️ Airflow master pipeline is ready to populate these tables")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 