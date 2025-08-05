#!/usr/bin/env python3
"""
Setup Morning Maghreb Database Schema
Sets up the complete database schema in the new Supabase database
"""

import os
import sys
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase configuration for new database
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

def read_schema_file():
    """Read the complete schema file"""
    schema_file = Path(__file__).parent.parent / "database" / "complete_supabase_schema.sql"
    
    if not schema_file.exists():
        logger.error(f"❌ Schema file not found: {schema_file}")
        return None
    
    with open(schema_file, 'r') as f:
        return f.read()

def setup_database_schema():
    """Set up the complete database schema"""
    logger.info("🚀 Setting up Morning Maghreb database schema...")
    
    # Read schema
    schema_sql = read_schema_file()
    if not schema_sql:
        return False
    
    # Split into individual statements
    statements = []
    current_statement = ""
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            current_statement += line + " "
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
    
    logger.info(f"📋 Found {len(statements)} SQL statements to execute")
    
    # Execute statements
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            logger.info(f"🔧 Executing statement {i}/{len(statements)}...")
            
            # Use RPC to execute SQL
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"sql": statement}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Statement {i} executed successfully")
                success_count += 1
            else:
                logger.warning(f"⚠️ Statement {i} failed: {response.status_code} - {response.text}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"❌ Error executing statement {i}: {e}")
            error_count += 1
    
    logger.info(f"📊 Schema setup completed:")
    logger.info(f"  ✅ Successful: {success_count}")
    logger.info(f"  ❌ Failed: {error_count}")
    
    return error_count == 0

def verify_schema_setup():
    """Verify that key tables exist"""
    logger.info("🔍 Verifying schema setup...")
    
    test_tables = [
        "profiles",
        "companies", 
        "watchlists",
        "watchlist_items",
        "price_alerts",
        "sentiment_votes",
        "newsletter_subscribers",
        "contests",
        "paper_trading_accounts",
        "portfolios"
    ]
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    existing_tables = []
    missing_tables = []
    
    for table in test_tables:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Table '{table}' exists")
                existing_tables.append(table)
            else:
                logger.warning(f"⚠️ Table '{table}' missing: {response.status_code}")
                missing_tables.append(table)
                
        except Exception as e:
            logger.error(f"❌ Error checking table '{table}': {e}")
            missing_tables.append(table)
    
    logger.info(f"📊 Schema verification completed:")
    logger.info(f"  ✅ Existing tables: {len(existing_tables)}")
    logger.info(f"  ❌ Missing tables: {len(missing_tables)}")
    
    if missing_tables:
        logger.warning(f"⚠️ Missing tables: {', '.join(missing_tables)}")
        return False
    
    return True

def main():
    """Main function"""
    logger.info("🚀 Morning Maghreb Database Schema Setup")
    logger.info("=" * 50)
    
    # Set up schema
    if setup_database_schema():
        logger.info("✅ Schema setup completed successfully")
        
        # Verify setup
        if verify_schema_setup():
            logger.info("✅ Schema verification passed")
            logger.info("🎉 Database is ready for Morning Maghreb!")
        else:
            logger.error("❌ Schema verification failed")
            return False
    else:
        logger.error("❌ Schema setup failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 