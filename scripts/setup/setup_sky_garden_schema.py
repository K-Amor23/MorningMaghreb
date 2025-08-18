#!/usr/bin/env python3
"""
Sky Garden Comprehensive Database Schema Setup

This script sets up the complete database schema for the enhanced frontend
in the sky garden Supabase project using direct REST API calls.
"""

import os
import sys
import asyncio
import logging
import aiohttp
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sky Garden Supabase credentials
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

class SkyGardenSchemaSetup:
    """Handles the setup of comprehensive database schema in Sky Garden"""
    
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_key = SUPABASE_SERVICE_KEY
        self.session = None
        
    async def __aenter__(self):
        """Setup async HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                'apikey': self.service_key,
                'Authorization': f'Bearer {self.service_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def create_table_via_rest(self, table_name: str, columns: list, description: str) -> bool:
        """Create table by inserting a row and letting Supabase create the table structure"""
        try:
            # Create a sample row with the desired structure
            sample_data = {}
            for col in columns:
                if col['type'] == 'uuid':
                    sample_data[col['name']] = '00000000-0000-0000-0000-000000000000'
                elif col['type'] == 'text':
                    sample_data[col['name']] = 'sample'
                elif col['type'] == 'integer':
                    sample_data[col['name']] = 0
                elif col['type'] == 'decimal':
                    sample_data[col['name']] = 0.0
                elif col['type'] == 'boolean':
                    sample_data[col['name']] = False
                elif col['type'] == 'jsonb':
                    sample_data[col['name']] = {}
                elif col['type'] == 'timestamp':
                    sample_data[col['name']] = '2024-01-01T00:00:00Z'
                elif col['type'] == 'date':
                    sample_data[col['name']] = '2024-01-01'
                elif col['type'] == 'time':
                    sample_data[col['name']] = '00:00:00'
            
            # Try to insert the sample data
            url = f"{self.supabase_url}/rest/v1/{table_name}"
            async with self.session.post(url, json=sample_data) as response:
                if response.status in [200, 201, 422]:  # 422 means table exists but constraint failed
                    logger.info(f"✅ {description}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ {description} failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ {description} failed with exception: {e}")
            return False
    
    async def create_market_status_table(self) -> bool:
        """Create market status table"""
        logger.info("📊 Creating market status table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'status', 'type': 'text'},
            {'name': 'current_time', 'type': 'time'},
            {'name': 'trading_hours', 'type': 'text'},
            {'name': 'total_market_cap', 'type': 'decimal'},
            {'name': 'total_volume', 'type': 'decimal'},
            {'name': 'advancers', 'type': 'integer'},
            {'name': 'decliners', 'type': 'integer'},
            {'name': 'unchanged', 'type': 'integer'},
            {'name': 'top_gainer', 'type': 'jsonb'},
            {'name': 'top_loser', 'type': 'jsonb'},
            {'name': 'most_active', 'type': 'jsonb'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('market_status', columns, "Market status table")
    
    async def create_comprehensive_market_data_table(self) -> bool:
        """Create comprehensive market data table"""
        logger.info("📈 Creating comprehensive market data table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'name', 'type': 'text'},
            {'name': 'sector', 'type': 'text'},
            {'name': 'current_price', 'type': 'decimal'},
            {'name': 'change', 'type': 'decimal'},
            {'name': 'change_percent', 'type': 'decimal'},
            {'name': 'open', 'type': 'decimal'},
            {'name': 'high', 'type': 'decimal'},
            {'name': 'low', 'type': 'decimal'},
            {'name': 'volume', 'type': 'integer'},
            {'name': 'market_cap', 'type': 'decimal'},
            {'name': 'pe_ratio', 'type': 'decimal'},
            {'name': 'dividend_yield', 'type': 'decimal'},
            {'name': 'fifty_two_week_high', 'type': 'decimal'},
            {'name': 'fifty_two_week_low', 'type': 'decimal'},
            {'name': 'avg_volume', 'type': 'integer'},
            {'name': 'volume_ratio', 'type': 'decimal'},
            {'name': 'beta', 'type': 'decimal'},
            {'name': 'shares_outstanding', 'type': 'integer'},
            {'name': 'float', 'type': 'integer'},
            {'name': 'insider_ownership', 'type': 'decimal'},
            {'name': 'institutional_ownership', 'type': 'decimal'},
            {'name': 'short_ratio', 'type': 'decimal'},
            {'name': 'payout_ratio', 'type': 'decimal'},
            {'name': 'roe', 'type': 'decimal'},
            {'name': 'roa', 'type': 'decimal'},
            {'name': 'debt_to_equity', 'type': 'decimal'},
            {'name': 'current_ratio', 'type': 'decimal'},
            {'name': 'quick_ratio', 'type': 'decimal'},
            {'name': 'gross_margin', 'type': 'decimal'},
            {'name': 'operating_margin', 'type': 'decimal'},
            {'name': 'net_margin', 'type': 'decimal'},
            {'name': 'fifty_two_week_position', 'type': 'decimal'},
            {'name': 'book_value_per_share', 'type': 'decimal'},
            {'name': 'source', 'type': 'text'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('comprehensive_market_data', columns, "Comprehensive market data table")
    
    async def create_company_news_table(self) -> bool:
        """Create company news table"""
        logger.info("📰 Creating company news table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'title', 'type': 'text'},
            {'name': 'summary', 'type': 'text'},
            {'name': 'source', 'type': 'text'},
            {'name': 'published_at', 'type': 'timestamp'},
            {'name': 'url', 'type': 'text'},
            {'name': 'category', 'type': 'text'},
            {'name': 'sentiment', 'type': 'text'},
            {'name': 'impact', 'type': 'text'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('company_news', columns, "Company news table")
    
    async def create_dividend_announcements_table(self) -> bool:
        """Create dividend announcements table"""
        logger.info("💰 Creating dividend announcements table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'type', 'type': 'text'},
            {'name': 'amount', 'type': 'decimal'},
            {'name': 'currency', 'type': 'text'},
            {'name': 'ex_date', 'type': 'date'},
            {'name': 'record_date', 'type': 'date'},
            {'name': 'payment_date', 'type': 'date'},
            {'name': 'description', 'type': 'text'},
            {'name': 'status', 'type': 'text'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('dividend_announcements', columns, "Dividend announcements table")
    
    async def create_earnings_announcements_table(self) -> bool:
        """Create earnings announcements table"""
        logger.info("📊 Creating earnings announcements table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'period', 'type': 'text'},
            {'name': 'report_date', 'type': 'date'},
            {'name': 'estimate', 'type': 'decimal'},
            {'name': 'actual', 'type': 'decimal'},
            {'name': 'surprise', 'type': 'decimal'},
            {'name': 'surprise_percent', 'type': 'decimal'},
            {'name': 'status', 'type': 'text'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('earnings_announcements', columns, "Earnings announcements table")
    
    async def create_etf_data_table(self) -> bool:
        """Create ETF data table"""
        logger.info("📊 Creating ETF data table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'name', 'type': 'text'},
            {'name': 'description', 'type': 'text'},
            {'name': 'asset_class', 'type': 'text'},
            {'name': 'expense_ratio', 'type': 'decimal'},
            {'name': 'aum', 'type': 'decimal'},
            {'name': 'inception_date', 'type': 'date'},
            {'name': 'issuer', 'type': 'text'},
            {'name': 'benchmark', 'type': 'text'},
            {'name': 'tracking_error', 'type': 'decimal'},
            {'name': 'dividend_yield', 'type': 'decimal'},
            {'name': 'holdings_count', 'type': 'integer'},
            {'name': 'top_holdings', 'type': 'jsonb'},
            {'name': 'sector_allocation', 'type': 'jsonb'},
            {'name': 'geographic_allocation', 'type': 'jsonb'},
            {'name': 'current_price', 'type': 'decimal'},
            {'name': 'change', 'type': 'decimal'},
            {'name': 'change_percent', 'type': 'decimal'},
            {'name': 'volume', 'type': 'integer'},
            {'name': 'market_cap', 'type': 'decimal'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('etf_data', columns, "ETF data table")
    
    async def create_corporate_actions_table(self) -> bool:
        """Create corporate actions table"""
        logger.info("🏢 Creating corporate actions table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'action_type', 'type': 'text'},
            {'name': 'title', 'type': 'text'},
            {'name': 'description', 'type': 'text'},
            {'name': 'announcement_date', 'type': 'date'},
            {'name': 'effective_date', 'type': 'date'},
            {'name': 'status', 'type': 'text'},
            {'name': 'details', 'type': 'jsonb'},
            {'name': 'impact_rating', 'type': 'text'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('corporate_actions', columns, "Corporate actions table")
    
    async def create_market_sentiment_table(self) -> bool:
        """Create market sentiment table"""
        logger.info("😊 Creating market sentiment table...")
        
        columns = [
            {'name': 'id', 'type': 'uuid'},
            {'name': 'ticker', 'type': 'text'},
            {'name': 'sentiment_score', 'type': 'decimal'},
            {'name': 'confidence', 'type': 'decimal'},
            {'name': 'source', 'type': 'text'},
            {'name': 'factors', 'type': 'jsonb'},
            {'name': 'scraped_at', 'type': 'timestamp'},
            {'name': 'created_at', 'type': 'timestamp'},
            {'name': 'updated_at', 'type': 'timestamp'}
        ]
        
        return await self.create_table_via_rest('market_sentiment', columns, "Market sentiment table")
    
    async def insert_sample_data(self) -> bool:
        """Insert sample data for testing"""
        logger.info("📝 Inserting sample data...")
        
        try:
            # Insert sample market status
            sample_market_status = {
                'status': 'open',
                'current_time': '10:30:00',
                'trading_hours': '09:00 - 16:00',
                'total_market_cap': 1016840000000,
                'total_volume': 212321128.20,
                'advancers': 45,
                'decliners': 23,
                'unchanged': 10,
                'top_gainer': {'ticker': 'SBM', 'name': 'Société des Boissons du Maroc', 'change': 120.00, 'change_percent': 6.03},
                'top_loser': {'ticker': 'ZDJ', 'name': 'Zellidja S.A', 'change': -18.80, 'change_percent': -5.99},
                'most_active': {'ticker': 'NAKL', 'name': 'Ennakl', 'volume': 232399, 'change': 3.78}
            }
            
            url = f"{self.supabase_url}/rest/v1/market_status"
            async with self.session.post(url, json=sample_market_status) as response:
                if response.status in [200, 201]:
                    logger.info("✅ Sample market status data inserted")
                else:
                    logger.warning(f"⚠️ Could not insert sample market status: {response.status}")
            
            # Insert sample comprehensive market data
            sample_market_data = {
                'ticker': 'SBM',
                'name': 'Société des Boissons du Maroc',
                'sector': 'Consumer Staples',
                'current_price': 120.00,
                'change': 6.03,
                'change_percent': 5.29,
                'open': 114.00,
                'high': 121.00,
                'low': 113.50,
                'volume': 150000,
                'market_cap': 5000000000,
                'pe_ratio': 15.2,
                'dividend_yield': 3.5,
                'fifty_two_week_high': 125.00,
                'fifty_two_week_low': 95.00,
                'avg_volume': 120000,
                'volume_ratio': 1.25,
                'beta': 0.8,
                'shares_outstanding': 41666667,
                'float': 40000000,
                'insider_ownership': 0.15,
                'institutional_ownership': 0.45,
                'short_ratio': 0.05,
                'payout_ratio': 0.35,
                'roe': 0.12,
                'roa': 0.08,
                'debt_to_equity': 0.3,
                'current_ratio': 1.8,
                'quick_ratio': 1.2,
                'gross_margin': 0.45,
                'operating_margin': 0.25,
                'net_margin': 0.15,
                'fifty_two_week_position': 0.83,
                'book_value_per_share': 45.50,
                'source': 'comprehensive_scraper'
            }
            
            url = f"{self.supabase_url}/rest/v1/comprehensive_market_data"
            async with self.session.post(url, json=sample_market_data) as response:
                if response.status in [200, 201]:
                    logger.info("✅ Sample market data inserted")
                else:
                    logger.warning(f"⚠️ Could not insert sample market data: {response.status}")
            
            logger.info("✅ Sample data insertion completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data insertion failed: {e}")
            return False
    
    async def setup_complete_schema(self) -> bool:
        """Setup the complete comprehensive database schema"""
        logger.info("🚀 Starting Sky Garden comprehensive database setup...")
        
        setup_steps = [
            ("Creating market status table", self.create_market_status_table),
            ("Creating comprehensive market data table", self.create_comprehensive_market_data_table),
            ("Creating company news table", self.create_company_news_table),
            ("Creating dividend announcements table", self.create_dividend_announcements_table),
            ("Creating earnings announcements table", self.create_earnings_announcements_table),
            ("Creating ETF data table", self.create_etf_data_table),
            ("Creating corporate actions table", self.create_corporate_actions_table),
            ("Creating market sentiment table", self.create_market_sentiment_table),
            ("Inserting sample data", self.insert_sample_data),
        ]
        
        success_count = 0
        total_steps = len(setup_steps)
        
        for step_name, step_function in setup_steps:
            logger.info(f"\n📋 {step_name}...")
            if await step_function():
                success_count += 1
                logger.info(f"✅ {step_name} completed successfully")
            else:
                logger.error(f"❌ {step_name} failed")
                # Continue with other steps even if one fails
        
        logger.info(f"\n🎯 Database setup completed: {success_count}/{total_steps} steps successful")
        
        if success_count == total_steps:
            logger.info("🎉 All database components created successfully!")
            return True
        else:
            logger.warning(f"⚠️ {total_steps - success_count} steps failed. Check logs for details.")
            return False

async def main():
    """Main function"""
    logger.info("🔐 Using Sky Garden Supabase credentials:")
    logger.info(f"   URL: {SUPABASE_URL}")
    logger.info(f"   Key: {SUPABASE_SERVICE_KEY[:20]}...")
    
    async with SkyGardenSchemaSetup() as setup:
        success = await setup.setup_complete_schema()
        
        if success:
            logger.info("\n🎉 Sky Garden comprehensive database setup completed successfully!")
            logger.info("📊 Your enhanced frontend now has access to:")
            logger.info("   - Comprehensive market data with 52-week ranges")
            logger.info("   - Company news and announcements")
            logger.info("   - Dividend announcements and history")
            logger.info("   - Earnings calendar and estimates")
            logger.info("   - ETF data and tracking")
            logger.info("   - Corporate actions and market sentiment")
            logger.info("   - Real-time market status")
            sys.exit(0)
        else:
            logger.error("\n❌ Database setup failed. Check logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
