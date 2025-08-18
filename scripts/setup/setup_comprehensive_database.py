#!/usr/bin/env python3
"""
Comprehensive Database Setup Script

This script sets up the complete database schema for the enhanced frontend,
including all tables, indexes, views, and functions needed for comprehensive
market data, news, dividends, earnings, and market status.

Usage:
    python setup_comprehensive_database.py [--supabase-url URL] [--supabase-key KEY]
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional, List
import aiohttp
import json

# Load env from project root .env.local if present (source of truth)
def _load_env_from_env_local() -> None:
    try:
        project_root = Path(__file__).resolve().parents[2]
        env_file = project_root / '.env.local'
        if env_file.exists():
            for raw in env_file.read_text().splitlines():
                line = raw.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Non-fatal
        pass

# Ensure env is loaded first
_load_env_from_env_local()

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent / 'apps' / 'backend'))

try:
    from database.connection import get_supabase_client
except ImportError:
    print("Warning: Could not import database connection module")
    get_supabase_client = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveDatabaseSetup:
    """Handles the setup of comprehensive database schema"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.session = None
        
    async def __aenter__(self):
        """Setup async HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def execute_sql(self, sql: str, description: str) -> bool:
        """Execute SQL statement via Supabase REST API"""
        try:
            url = f"{self.supabase_url}/rest/v1/rpc/exec_sql"
            
            payload = {
                "query": sql
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ {description}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ {description} failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ {description} failed with exception: {e}")
            return False
    
    async def create_extensions(self) -> bool:
        """Create necessary PostgreSQL extensions"""
        logger.info("🔧 Creating PostgreSQL extensions...")
        
        extensions = [
            ("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";", "uuid-ossp extension"),
            ("CREATE EXTENSION IF NOT EXISTS \"timescaledb\";", "timescaledb extension")
        ]
        
        success_count = 0
        for sql, description in extensions:
            if await self.execute_sql(sql, description):
                success_count += 1
        
        return success_count == len(extensions)
    
    async def create_market_status_table(self) -> bool:
        """Create market status table"""
        logger.info("📊 Creating market status table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS market_status (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'closed', 'pre_market', 'after_hours')),
            current_time TIME NOT NULL,
            trading_hours VARCHAR(50) NOT NULL,
            total_market_cap DECIMAL(20,2) NOT NULL,
            total_volume DECIMAL(20,2) NOT NULL,
            advancers INTEGER NOT NULL DEFAULT 0,
            decliners INTEGER NOT NULL DEFAULT 0,
            unchanged INTEGER NOT NULL DEFAULT 0,
            top_gainer JSONB NOT NULL,
            top_loser JSONB NOT NULL,
            most_active JSONB NOT NULL,
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Market status table")
    
    async def create_comprehensive_market_data_table(self) -> bool:
        """Create comprehensive market data table"""
        logger.info("📈 Creating comprehensive market data table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS comprehensive_market_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            name VARCHAR(255) NOT NULL,
            sector VARCHAR(100),
            current_price DECIMAL(10,2) NOT NULL,
            change DECIMAL(10,2) NOT NULL,
            change_percent DECIMAL(8,4) NOT NULL,
            open DECIMAL(10,2),
            high DECIMAL(10,2),
            low DECIMAL(10,2),
            volume BIGINT,
            market_cap DECIMAL(20,2),
            pe_ratio DECIMAL(8,2),
            dividend_yield DECIMAL(6,4),
            fifty_two_week_high DECIMAL(10,2),
            fifty_two_week_low DECIMAL(10,2),
            avg_volume BIGINT,
            volume_ratio DECIMAL(8,4),
            beta DECIMAL(6,4),
            shares_outstanding BIGINT,
            float BIGINT,
            insider_ownership DECIMAL(6,4),
            institutional_ownership DECIMAL(6,4),
            short_ratio DECIMAL(8,4),
            payout_ratio DECIMAL(6,4),
            roe DECIMAL(8,4),
            roa DECIMAL(8,4),
            debt_to_equity DECIMAL(8,4),
            current_ratio DECIMAL(8,4),
            quick_ratio DECIMAL(8,4),
            gross_margin DECIMAL(6,4),
            operating_margin DECIMAL(6,4),
            net_margin DECIMAL(6,4),
            fifty_two_week_position DECIMAL(6,4),
            book_value_per_share DECIMAL(10,4),
            source VARCHAR(100) DEFAULT 'comprehensive_scraper',
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Comprehensive market data table")
    
    async def create_company_news_table(self) -> bool:
        """Create company news table"""
        logger.info("📰 Creating company news table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS company_news (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            source VARCHAR(100) NOT NULL,
            published_at TIMESTAMPTZ NOT NULL,
            url TEXT,
            category VARCHAR(50) NOT NULL CHECK (category IN ('news', 'announcement', 'earnings', 'dividend', 'corporate_action')),
            sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('positive', 'negative', 'neutral')),
            impact VARCHAR(20) NOT NULL CHECK (impact IN ('high', 'medium', 'low')),
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Company news table")
    
    async def create_dividend_announcements_table(self) -> bool:
        """Create dividend announcements table"""
        logger.info("💰 Creating dividend announcements table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS dividend_announcements (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            type VARCHAR(50) NOT NULL CHECK (type IN ('dividend', 'stock_split', 'rights_issue')),
            amount DECIMAL(10,4) NOT NULL,
            currency VARCHAR(3) NOT NULL DEFAULT 'MAD',
            ex_date DATE NOT NULL,
            record_date DATE,
            payment_date DATE,
            description TEXT,
            status VARCHAR(20) NOT NULL CHECK (status IN ('announced', 'ex_dividend', 'paid')),
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Dividend announcements table")
    
    async def create_earnings_announcements_table(self) -> bool:
        """Create earnings announcements table"""
        logger.info("📊 Creating earnings announcements table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS earnings_announcements (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            period VARCHAR(20) NOT NULL,
            report_date DATE NOT NULL,
            estimate DECIMAL(10,4),
            actual DECIMAL(10,4),
            surprise DECIMAL(10,4),
            surprise_percent DECIMAL(8,4),
            status VARCHAR(20) NOT NULL CHECK (status IN ('scheduled', 'reported', 'missed')),
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Earnings announcements table")
    
    async def create_etf_data_table(self) -> bool:
        """Create ETF data table"""
        logger.info("📊 Creating ETF data table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS etf_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            asset_class VARCHAR(100),
            expense_ratio DECIMAL(6,4),
            aum DECIMAL(20,2),
            inception_date DATE,
            issuer VARCHAR(100),
            benchmark VARCHAR(100),
            tracking_error DECIMAL(6,4),
            dividend_yield DECIMAL(6,4),
            holdings_count INTEGER,
            top_holdings JSONB,
            sector_allocation JSONB,
            geographic_allocation JSONB,
            current_price DECIMAL(10,4),
            change DECIMAL(10,4),
            change_percent DECIMAL(8,4),
            volume BIGINT,
            market_cap DECIMAL(20,2),
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "ETF data table")
    
    async def create_corporate_actions_table(self) -> bool:
        """Create corporate actions table"""
        logger.info("🏢 Creating corporate actions table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS corporate_actions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10) NOT NULL,
            action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('merger', 'acquisition', 'spin_off', 'bankruptcy', 'delisting', 'listing', 'name_change')),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            announcement_date DATE NOT NULL,
            effective_date DATE,
            status VARCHAR(20) NOT NULL CHECK (status IN ('announced', 'pending', 'completed', 'cancelled')),
            details JSONB,
            impact_rating VARCHAR(20) CHECK (impact_rating IN ('high', 'medium', 'low')),
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Corporate actions table")
    
    async def create_market_sentiment_table(self) -> bool:
        """Create market sentiment table"""
        logger.info("😊 Creating market sentiment table...")
        
        sql = """
        CREATE TABLE IF NOT EXISTS market_sentiment (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker VARCHAR(10),
            sentiment_score DECIMAL(4,3) NOT NULL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
            confidence DECIMAL(4,3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            source VARCHAR(100) NOT NULL,
            factors JSONB,
            scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        return await self.execute_sql(sql, "Market sentiment table")
    
    async def create_indexes(self) -> bool:
        """Create all necessary indexes"""
        logger.info("🔍 Creating database indexes...")
        
        # Market status indexes
        indexes = [
            ("CREATE INDEX IF NOT EXISTS idx_market_status_scraped_at ON market_status(scraped_at);", "Market status scraped_at index"),
            
            # Comprehensive market data indexes
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_ticker ON comprehensive_market_data(ticker);", "Market data ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_scraped_at ON comprehensive_market_data(scraped_at);", "Market data scraped_at index"),
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_sector ON comprehensive_market_data(sector);", "Market data sector index"),
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_change_percent ON comprehensive_market_data(change_percent);", "Market data change_percent index"),
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_volume ON comprehensive_market_data(volume);", "Market data volume index"),
            ("CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_market_cap ON comprehensive_market_data(market_cap);", "Market data market_cap index"),
            
            # Company news indexes
            ("CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);", "Company news ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);", "Company news published_at index"),
            ("CREATE INDEX IF NOT EXISTS idx_company_news_category ON company_news(category);", "Company news category index"),
            ("CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);", "Company news sentiment index"),
            ("CREATE INDEX IF NOT EXISTS idx_company_news_scraped_at ON company_news(scraped_at);", "Company news scraped_at index"),
            
            # Dividend announcements indexes
            ("CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ticker ON dividend_announcements(ticker);", "Dividend announcements ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ex_date ON dividend_announcements(ex_date);", "Dividend announcements ex_date index"),
            ("CREATE INDEX IF NOT EXISTS idx_dividend_announcements_status ON dividend_announcements(status);", "Dividend announcements status index"),
            ("CREATE INDEX IF NOT EXISTS idx_dividend_announcements_scraped_at ON dividend_announcements(scraped_at);", "Dividend announcements scraped_at index"),
            
            # Earnings announcements indexes
            ("CREATE INDEX IF NOT EXISTS idx_earnings_announcements_ticker ON earnings_announcements(ticker);", "Earnings announcements ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_earnings_announcements_report_date ON earnings_announcements(report_date);", "Earnings announcements report_date index"),
            ("CREATE INDEX IF NOT EXISTS idx_earnings_announcements_status ON earnings_announcements(status);", "Earnings announcements status index"),
            ("CREATE INDEX IF NOT EXISTS idx_earnings_announcements_scraped_at ON earnings_announcements(scraped_at);", "Earnings announcements scraped_at index"),
            
            # ETF data indexes
            ("CREATE INDEX IF NOT EXISTS idx_etf_data_ticker ON etf_data(ticker);", "ETF data ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_etf_data_asset_class ON etf_data(asset_class);", "ETF data asset_class index"),
            ("CREATE INDEX IF NOT EXISTS idx_etf_data_scraped_at ON etf_data(scraped_at);", "ETF data scraped_at index"),
            
            # Corporate actions indexes
            ("CREATE INDEX IF NOT EXISTS idx_corporate_actions_ticker ON corporate_actions(ticker);", "Corporate actions ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_corporate_actions_action_type ON corporate_actions(action_type);", "Corporate actions action_type index"),
            ("CREATE INDEX IF NOT EXISTS idx_corporate_actions_announcement_date ON corporate_actions(announcement_date);", "Corporate actions announcement_date index"),
            ("CREATE INDEX IF NOT EXISTS idx_corporate_actions_status ON corporate_actions(status);", "Corporate actions status index"),
            ("CREATE INDEX IF NOT EXISTS idx_corporate_actions_scraped_at ON corporate_actions(scraped_at);", "Corporate actions scraped_at index"),
            
            # Market sentiment indexes
            ("CREATE INDEX IF NOT EXISTS idx_market_sentiment_ticker ON market_sentiment(ticker);", "Market sentiment ticker index"),
            ("CREATE INDEX IF NOT EXISTS idx_market_sentiment_sentiment_score ON market_sentiment(sentiment_score);", "Market sentiment sentiment_score index"),
            ("CREATE INDEX IF NOT EXISTS idx_market_sentiment_scraped_at ON market_sentiment(scraped_at);", "Market sentiment scraped_at index"),
        ]
        
        success_count = 0
        for sql, description in indexes:
            if await self.execute_sql(sql, description):
                success_count += 1
        
        return success_count == len(indexes)
    
    async def create_views(self) -> bool:
        """Create database views"""
        logger.info("👁️ Creating database views...")
        
        views = [
            # Market overview view
            ("""
            CREATE OR REPLACE VIEW market_overview AS
            SELECT 
                ms.status,
                ms.current_time,
                ms.trading_hours,
                ms.total_market_cap,
                ms.total_volume,
                ms.advancers,
                ms.decliners,
                ms.unchanged,
                ms.top_gainer,
                ms.top_loser,
                ms.most_active,
                ms.scraped_at
            FROM market_status ms
            WHERE ms.scraped_at = (
                SELECT MAX(scraped_at) 
                FROM market_status
            );
            """, "Market overview view"),
            
            # Top movers view
            ("""
            CREATE OR REPLACE VIEW top_movers AS
            SELECT 
                ticker,
                name,
                current_price,
                change,
                change_percent,
                volume,
                scraped_at
            FROM comprehensive_market_data
            WHERE scraped_at = (
                SELECT MAX(scraped_at) 
                FROM comprehensive_market_data 
                WHERE ticker = comprehensive_market_data.ticker
            )
            ORDER BY ABS(change_percent) DESC;
            """, "Top movers view"),
            
            # Sector performance view
            ("""
            CREATE OR REPLACE VIEW sector_performance AS
            SELECT 
                sector,
                COUNT(*) as company_count,
                AVG(change_percent) as avg_change,
                SUM(CASE WHEN change_percent > 0 THEN 1 ELSE 0 END) as advancers,
                SUM(CASE WHEN change_percent < 0 THEN 1 ELSE 0 END) as decliners
            FROM comprehensive_market_data
            WHERE scraped_at = (
                SELECT MAX(scraped_at) 
                FROM comprehensive_market_data 
                WHERE ticker = comprehensive_market_data.ticker
            )
                AND sector IS NOT NULL
            GROUP BY sector
            ORDER BY avg_change DESC;
            """, "Sector performance view"),
        ]
        
        success_count = 0
        for sql, description in views:
            if await self.execute_sql(sql, description):
                success_count += 1
        
        return success_count == len(views)
    
    async def create_functions(self) -> bool:
        """Create database functions"""
        logger.info("⚙️ Creating database functions...")
        
        functions = [
            # Update updated_at trigger function
            ("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """, "Update updated_at trigger function"),
            
            # Get comprehensive ticker data function
            ("""
            CREATE OR REPLACE FUNCTION get_comprehensive_ticker_data(p_ticker VARCHAR)
            RETURNS TABLE (
                ticker VARCHAR,
                market_data JSONB,
                news JSONB,
                dividends JSONB,
                earnings JSONB
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    p_ticker::VARCHAR as ticker,
                    (SELECT row_to_json(cmd.*)::JSONB 
                     FROM comprehensive_market_data cmd 
                     WHERE cmd.ticker = p_ticker 
                     ORDER BY cmd.scraped_at DESC 
                     LIMIT 1) as market_data,
                    (SELECT COALESCE(json_agg(row_to_json(cn.*)), '[]'::JSON)::JSONB 
                     FROM company_news cn 
                     WHERE cn.ticker = p_ticker 
                     ORDER BY cn.published_at DESC 
                     LIMIT 10) as news,
                    (SELECT COALESCE(json_agg(row_to_json(da.*)), '[]'::JSON)::JSONB 
                     FROM dividend_announcements da 
                     WHERE da.ticker = p_ticker 
                     ORDER BY da.ex_date DESC 
                     LIMIT 10) as dividends,
                    (SELECT COALESCE(json_agg(row_to_json(ea.*)), '[]'::JSON)::JSONB 
                     FROM earnings_announcements ea 
                     WHERE ea.ticker = p_ticker 
                     ORDER BY ea.report_date DESC 
                     LIMIT 10) as earnings;
            END;
            $$ LANGUAGE plpgsql;
            """, "Get comprehensive ticker data function"),
            
            # Get market overview function
            ("""
            CREATE OR REPLACE FUNCTION get_market_overview()
            RETURNS TABLE (
                market_status JSONB,
                top_gainers JSONB,
                top_losers JSONB,
                most_active JSONB,
                sector_performance JSONB,
                recent_news JSONB,
                upcoming_dividends JSONB,
                upcoming_earnings JSONB
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    (SELECT row_to_json(ms.*)::JSONB 
                     FROM market_status ms 
                     ORDER BY ms.scraped_at DESC 
                     LIMIT 1) as market_status,
                    (SELECT COALESCE(json_agg(row_to_json(tg.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, name, current_price, change, change_percent, volume
                         FROM comprehensive_market_data
                         WHERE scraped_at = (SELECT MAX(scraped_at) FROM comprehensive_market_data)
                         ORDER BY change_percent DESC
                         LIMIT 5
                     ) tg) as top_gainers,
                    (SELECT COALESCE(json_agg(row_to_json(tl.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, name, current_price, change, change_percent, volume
                         FROM comprehensive_market_data
                         WHERE scraped_at = (SELECT MAX(scraped_at) FROM comprehensive_market_data)
                         ORDER BY change_percent ASC
                         LIMIT 5
                     ) tl) as top_losers,
                    (SELECT COALESCE(json_agg(row_to_json(ma.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, name, current_price, volume, change
                         FROM comprehensive_market_data
                         WHERE scraped_at = (SELECT MAX(scraped_at) FROM comprehensive_market_data)
                         ORDER BY volume DESC
                         LIMIT 10
                     ) ma) as most_active,
                    (SELECT COALESCE(json_object_agg(sector, performance), '{}'::JSON)::JSONB 
                     FROM (
                         SELECT 
                             sector,
                             json_build_object(
                                 'count', COUNT(*),
                                 'totalChange', SUM(change_percent),
                                 'avgChange', AVG(change_percent)
                             ) as performance
                         FROM comprehensive_market_data
                         WHERE scraped_at = (SELECT MAX(scraped_at) FROM comprehensive_market_data)
                             AND sector IS NOT NULL
                         GROUP BY sector
                     ) sp) as sector_performance,
                    (SELECT COALESCE(json_agg(row_to_json(rn.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, title, published_at, category, impact
                         FROM company_news
                         ORDER BY published_at DESC
                         LIMIT 15
                     ) rn) as recent_news,
                    (SELECT COALESCE(json_agg(row_to_json(ud.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, amount, ex_date, type
                         FROM dividend_announcements
                         WHERE ex_date >= CURRENT_DATE
                         ORDER BY ex_date ASC
                         LIMIT 10
                     ) ud) as upcoming_dividends,
                    (SELECT COALESCE(json_agg(row_to_json(ue.*)), '[]'::JSON)::JSONB 
                     FROM (
                         SELECT ticker, period, report_date, estimate
                         FROM earnings_announcements
                         WHERE report_date >= CURRENT_DATE
                         ORDER BY report_date ASC
                         LIMIT 10
                     ) ue) as upcoming_earnings;
            END;
            $$ LANGUAGE plpgsql;
            """, "Get market overview function"),
        ]
        
        success_count = 0
        for sql, description in functions:
            if await self.execute_sql(sql, description):
                success_count += 1
        
        return success_count == len(functions)
    
    async def create_triggers(self) -> bool:
        """Create database triggers"""
        logger.info("🔔 Creating database triggers...")
        
        triggers = [
            # Comprehensive market data trigger
            ("""
            CREATE TRIGGER update_comprehensive_market_data_updated_at 
                BEFORE UPDATE ON comprehensive_market_data 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Comprehensive market data updated_at trigger"),
            
            # Market status trigger
            ("""
            CREATE TRIGGER update_market_status_updated_at 
                BEFORE UPDATE ON market_status 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Market status updated_at trigger"),
            
            # Company news trigger
            ("""
            CREATE TRIGGER update_company_news_updated_at 
                BEFORE UPDATE ON company_news 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Company news updated_at trigger"),
            
            # Dividend announcements trigger
            ("""
            CREATE TRIGGER update_dividend_announcements_updated_at 
                BEFORE UPDATE ON dividend_announcements 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Dividend announcements updated_at trigger"),
            
            # Earnings announcements trigger
            ("""
            CREATE TRIGGER update_earnings_announcements_updated_at 
                BEFORE UPDATE ON earnings_announcements 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Earnings announcements updated_at trigger"),
            
            # ETF data trigger
            ("""
            CREATE TRIGGER update_etf_data_updated_at 
                BEFORE UPDATE ON etf_data 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "ETF data updated_at trigger"),
            
            # Corporate actions trigger
            ("""
            CREATE TRIGGER update_corporate_actions_updated_at 
                BEFORE UPDATE ON corporate_actions 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Corporate actions updated_at trigger"),
            
            # Market sentiment trigger
            ("""
            CREATE TRIGGER update_market_sentiment_updated_at 
                BEFORE UPDATE ON market_sentiment 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """, "Market sentiment updated_at trigger"),
        ]
        
        success_count = 0
        for trigger_sql, description in triggers:
            if await self.execute_sql(trigger_sql, description):
                success_count += 1
        
        return success_count == len(triggers)
    
    async def insert_sample_data(self) -> bool:
        """Insert sample data for testing"""
        logger.info("📝 Inserting sample data...")
        
        sample_market_status = """
        INSERT INTO market_status (
            status, current_time, trading_hours, total_market_cap, total_volume,
            advancers, decliners, unchanged, top_gainer, top_loser, most_active
        ) VALUES (
            'open',
            '10:30:00',
            '09:00 - 16:00',
            1016840000000,
            212321128.20,
            45,
            23,
            10,
            '{"ticker": "SBM", "name": "Société des Boissons du Maroc", "change": 120.00, "change_percent": 6.03}',
            '{"ticker": "ZDJ", "name": "Zellidja S.A", "change": -18.80, "change_percent": -5.99}',
            '{"ticker": "NAKL", "name": "Ennakl", "volume": 232399, "change": 3.78}'
        ) ON CONFLICT DO NOTHING;
        """
        
        return await self.execute_sql(sample_market_status, "Sample market status data")
    
    async def setup_complete_database(self) -> bool:
        """Setup the complete comprehensive database"""
        logger.info("🚀 Starting comprehensive database setup...")
        
        setup_steps = [
            ("Creating extensions", self.create_extensions),
            ("Creating market status table", self.create_market_status_table),
            ("Creating comprehensive market data table", self.create_comprehensive_market_data_table),
            ("Creating company news table", self.create_company_news_table),
            ("Creating dividend announcements table", self.create_dividend_announcements_table),
            ("Creating earnings announcements table", self.create_earnings_announcements_table),
            ("Creating ETF data table", self.create_etf_data_table),
            ("Creating corporate actions table", self.create_corporate_actions_table),
            ("Creating market sentiment table", self.create_market_sentiment_table),
            ("Creating indexes", self.create_indexes),
            ("Creating views", self.create_views),
            ("Creating functions", self.create_functions),
            ("Creating triggers", self.create_triggers),
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
    parser = argparse.ArgumentParser(description='Setup comprehensive database schema')
    parser.add_argument('--supabase-url', help='Supabase URL')
    parser.add_argument('--supabase-key', help='Supabase service role key')
    
    args = parser.parse_args()
    
    # Get credentials from environment or arguments
    supabase_url = args.supabase_url or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = args.supabase_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials. Please provide --supabase-url and --supabase-key or set environment variables.")
        sys.exit(1)
    
    logger.info("🔐 Using Supabase credentials:")
    logger.info(f"   URL: {supabase_url}")
    logger.info(f"   Key: {supabase_key[:20]}...")
    
    async with ComprehensiveDatabaseSetup(supabase_url, supabase_key) as setup:
        success = await setup.setup_complete_database()
        
        if success:
            logger.info("\n🎉 Comprehensive database setup completed successfully!")
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
