-- Sky Garden Comprehensive Database Schema (Safe Version)
-- Run this script in your Supabase dashboard SQL editor
-- This script safely handles existing tables and columns

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Market Status Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'market_status') THEN
        CREATE TABLE market_status (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            status TEXT NOT NULL,
            current_time_local TIME,
            trading_hours TEXT,
            total_market_cap DECIMAL(20,2),
            total_volume DECIMAL(20,2),
            advancers INTEGER,
            decliners INTEGER,
            unchanged INTEGER,
            top_gainer JSONB,
            top_loser JSONB,
            most_active JSONB,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created market_status table';
    ELSE
        RAISE NOTICE 'market_status table already exists';
    END IF;
END $$;

-- 2. Comprehensive Market Data Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'comprehensive_market_data') THEN
        CREATE TABLE comprehensive_market_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            name TEXT,
            sector TEXT,
            current_price DECIMAL(10,2),
            change DECIMAL(10,2),
            change_percent DECIMAL(10,4),
            open DECIMAL(10,2),
            high DECIMAL(10,2),
            low DECIMAL(10,2),
            volume BIGINT,
            market_cap DECIMAL(20,2),
            pe_ratio DECIMAL(10,4),
            dividend_yield DECIMAL(10,4),
            fifty_two_week_high DECIMAL(10,2),
            fifty_two_week_low DECIMAL(10,2),
            avg_volume BIGINT,
            volume_ratio DECIMAL(10,4),
            beta DECIMAL(10,4),
            shares_outstanding BIGINT,
            float BIGINT,
            insider_ownership DECIMAL(10,4),
            institutional_ownership DECIMAL(10,4),
            short_ratio DECIMAL(10,4),
            payout_ratio DECIMAL(10,4),
            roe DECIMAL(10,4),
            roa DECIMAL(10,4),
            debt_to_equity DECIMAL(10,4),
            current_ratio DECIMAL(10,4),
            quick_ratio DECIMAL(10,4),
            gross_margin DECIMAL(10,4),
            operating_margin DECIMAL(10,4),
            net_margin DECIMAL(10,4),
            fifty_two_week_position DECIMAL(10,4),
            book_value_per_share DECIMAL(10,2),
            source TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created comprehensive_market_data table';
    ELSE
        RAISE NOTICE 'comprehensive_market_data table already exists';
    END IF;
END $$;

-- 3. Company News Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'company_news') THEN
        CREATE TABLE company_news (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            source TEXT,
            published_at TIMESTAMP WITH TIME ZONE,
            url TEXT,
            category TEXT,
            sentiment TEXT,
            impact TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created company_news table';
    ELSE
        RAISE NOTICE 'company_news table already exists';
    END IF;
END $$;

-- 4. Dividend Announcements Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'dividend_announcements') THEN
        CREATE TABLE dividend_announcements (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            type TEXT,
            amount DECIMAL(10,4),
            currency TEXT DEFAULT 'MAD',
            ex_date DATE,
            record_date DATE,
            payment_date DATE,
            description TEXT,
            status TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created dividend_announcements table';
    ELSE
        RAISE NOTICE 'dividend_announcements table already exists';
    END IF;
END $$;

-- 5. Earnings Announcements Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'earnings_announcements') THEN
        CREATE TABLE earnings_announcements (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            period TEXT,
            report_date DATE,
            estimate DECIMAL(10,4),
            actual DECIMAL(10,4),
            surprise DECIMAL(10,4),
            surprise_percent DECIMAL(10,4),
            status TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created earnings_announcements table';
    ELSE
        RAISE NOTICE 'earnings_announcements table already exists';
    END IF;
END $$;

-- 6. ETF Data Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'etf_data') THEN
        CREATE TABLE etf_data (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            name TEXT,
            description TEXT,
            asset_class TEXT,
            expense_ratio DECIMAL(10,4),
            aum DECIMAL(20,2),
            inception_date DATE,
            issuer TEXT,
            benchmark TEXT,
            tracking_error DECIMAL(10,4),
            dividend_yield DECIMAL(10,4),
            holdings_count INTEGER,
            top_holdings JSONB,
            sector_allocation JSONB,
            geographic_allocation JSONB,
            current_price DECIMAL(10,2),
            change DECIMAL(10,2),
            change_percent DECIMAL(10,4),
            volume BIGINT,
            market_cap DECIMAL(20,2),
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created etf_data table';
    ELSE
        RAISE NOTICE 'etf_data table already exists';
    END IF;
END $$;

-- 7. Corporate Actions Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'corporate_actions') THEN
        CREATE TABLE corporate_actions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            action_type TEXT,
            title TEXT NOT NULL,
            description TEXT,
            announcement_date DATE,
            effective_date DATE,
            status TEXT,
            details JSONB,
            impact_rating TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created corporate_actions table';
    ELSE
        RAISE NOTICE 'corporate_actions table already exists';
    END IF;
END $$;

-- 8. Market Sentiment Table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'market_sentiment') THEN
        CREATE TABLE market_sentiment (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            ticker TEXT NOT NULL,
            sentiment_score DECIMAL(5,4),
            confidence DECIMAL(5,4),
            source TEXT,
            factors JSONB,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        RAISE NOTICE 'Created market_sentiment table';
    ELSE
        RAISE NOTICE 'market_sentiment table already exists';
    END IF;
END $$;

-- Create indexes for better performance (only if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_comprehensive_market_data_ticker') THEN
        CREATE INDEX idx_comprehensive_market_data_ticker ON comprehensive_market_data(ticker);
        RAISE NOTICE 'Created index idx_comprehensive_market_data_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_comprehensive_market_data_sector') THEN
        CREATE INDEX idx_comprehensive_market_data_sector ON comprehensive_market_data(sector);
        RAISE NOTICE 'Created index idx_comprehensive_market_data_sector';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_comprehensive_market_data_scraped_at') THEN
        CREATE INDEX idx_comprehensive_market_data_scraped_at ON comprehensive_market_data(scraped_at);
        RAISE NOTICE 'Created index idx_comprehensive_market_data_scraped_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_company_news_ticker') THEN
        CREATE INDEX idx_company_news_ticker ON company_news(ticker);
        RAISE NOTICE 'Created index idx_company_news_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_company_news_published_at') THEN
        CREATE INDEX idx_company_news_published_at ON company_news(published_at);
        RAISE NOTICE 'Created index idx_company_news_published_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_company_news_category') THEN
        CREATE INDEX idx_company_news_category ON company_news(category);
        RAISE NOTICE 'Created index idx_company_news_category';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_dividend_announcements_ticker') THEN
        CREATE INDEX idx_dividend_announcements_ticker ON dividend_announcements(ticker);
        RAISE NOTICE 'Created index idx_dividend_announcements_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_earnings_announcements_ticker') THEN
        CREATE INDEX idx_earnings_announcements_ticker ON earnings_announcements(ticker);
        RAISE NOTICE 'Created index idx_earnings_announcements_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_etf_data_ticker') THEN
        CREATE INDEX idx_etf_data_ticker ON etf_data(ticker);
        RAISE NOTICE 'Created index idx_etf_data_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_corporate_actions_ticker') THEN
        CREATE INDEX idx_corporate_actions_ticker ON corporate_actions(ticker);
        RAISE NOTICE 'Created index idx_corporate_actions_ticker';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_market_sentiment_ticker') THEN
        CREATE INDEX idx_market_sentiment_ticker ON market_sentiment(ticker);
        RAISE NOTICE 'Created index idx_market_sentiment_ticker';
    END IF;
END $$;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables (only if triggers don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_market_status_updated_at') THEN
        CREATE TRIGGER update_market_status_updated_at BEFORE UPDATE ON market_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_market_status_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_comprehensive_market_data_updated_at') THEN
        CREATE TRIGGER update_comprehensive_market_data_updated_at BEFORE UPDATE ON comprehensive_market_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_comprehensive_market_data_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_company_news_updated_at') THEN
        CREATE TRIGGER update_company_news_updated_at BEFORE UPDATE ON company_news FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_company_news_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_dividend_announcements_updated_at') THEN
        CREATE TRIGGER update_dividend_announcements_updated_at BEFORE UPDATE ON dividend_announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_dividend_announcements_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_earnings_announcements_updated_at') THEN
        CREATE TRIGGER update_earnings_announcements_updated_at BEFORE UPDATE ON earnings_announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_earnings_announcements_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_etf_data_updated_at') THEN
        CREATE TRIGGER update_etf_data_updated_at BEFORE UPDATE ON etf_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_etf_data_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_corporate_actions_updated_at') THEN
        CREATE TRIGGER update_corporate_actions_updated_at BEFORE UPDATE ON corporate_actions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_corporate_actions_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_market_sentiment_updated_at') THEN
        CREATE TRIGGER update_market_sentiment_updated_at BEFORE UPDATE ON market_sentiment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_market_sentiment_updated_at';
    END IF;
END $$;

-- Insert sample data for testing (only if tables are empty)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM market_status LIMIT 1) THEN
        INSERT INTO market_status (
            status, current_time_local, trading_hours, total_market_cap, total_volume,
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
        );
        RAISE NOTICE 'Inserted sample market status data';
    ELSE
        RAISE NOTICE 'Market status table already has data, skipping sample insert';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM comprehensive_market_data LIMIT 1) THEN
        INSERT INTO comprehensive_market_data (
            ticker, name, sector, current_price, change, change_percent, open, high, low,
            volume, market_cap, pe_ratio, dividend_yield, fifty_two_week_high, fifty_two_week_low,
            avg_volume, volume_ratio, beta, shares_outstanding, float, insider_ownership,
            institutional_ownership, short_ratio, payout_ratio, roe, roa, debt_to_equity,
            current_ratio, quick_ratio, gross_margin, operating_margin, net_margin,
            fifty_two_week_position, book_value_per_share, source
        ) VALUES (
            'SBM',
            'Société des Boissons du Maroc',
            'Consumer Staples',
            120.00,
            6.03,
            5.29,
            114.00,
            121.00,
            113.50,
            150000,
            5000000000,
            15.2,
            3.5,
            125.00,
            95.00,
            120000,
            1.25,
            0.8,
            41666667,
            40000000,
            0.15,
            0.45,
            0.05,
            0.35,
            0.12,
            0.08,
            0.3,
            1.8,
            1.2,
            0.45,
            0.25,
            0.15,
            0.83,
            45.50,
            'comprehensive_scraper'
        );
        RAISE NOTICE 'Inserted sample comprehensive market data';
    ELSE
        RAISE NOTICE 'Comprehensive market data table already has data, skipping sample insert';
    END IF;
END $$;

-- Enable Row Level Security (RLS) if not already enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'market_status' AND rowsecurity = true) THEN
        ALTER TABLE market_status ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on market_status';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'comprehensive_market_data' AND rowsecurity = true) THEN
        ALTER TABLE comprehensive_market_data ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on comprehensive_market_data';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'company_news' AND rowsecurity = true) THEN
        ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on company_news';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'dividend_announcements' AND rowsecurity = true) THEN
        ALTER TABLE dividend_announcements ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on dividend_announcements';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'earnings_announcements' AND rowsecurity = true) THEN
        ALTER TABLE earnings_announcements ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on earnings_announcements';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'etf_data' AND rowsecurity = true) THEN
        ALTER TABLE etf_data ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on etf_data';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'corporate_actions' AND rowsecurity = true) THEN
        ALTER TABLE corporate_actions ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on corporate_actions';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'market_sentiment' AND rowsecurity = true) THEN
        ALTER TABLE market_sentiment ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'Enabled RLS on market_sentiment';
    END IF;
END $$;

-- Create RLS policies (only if they don't exist)
DO $$
BEGIN
    -- Market Status policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_status' AND policyname = 'Allow public read access to market_status') THEN
        CREATE POLICY "Allow public read access to market_status" ON market_status FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for market_status read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_status' AND policyname = 'Allow authenticated users to insert market_status') THEN
        CREATE POLICY "Allow authenticated users to insert market_status" ON market_status FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for market_status insert access';
    END IF;
    
    -- Comprehensive Market Data policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'comprehensive_market_data' AND policyname = 'Allow public read access to comprehensive_market_data') THEN
        CREATE POLICY "Allow public read access to comprehensive_market_data" ON comprehensive_market_data FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for comprehensive_market_data read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'comprehensive_market_data' AND policyname = 'Allow authenticated users to insert comprehensive_market_data') THEN
        CREATE POLICY "Allow authenticated users to insert comprehensive_market_data" ON comprehensive_market_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for comprehensive_market_data insert access';
    END IF;
    
    -- Company News policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'company_news' AND policyname = 'Allow public read access to company_news') THEN
        CREATE POLICY "Allow public read access to company_news" ON company_news FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for company_news read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'company_news' AND policyname = 'Allow authenticated users to insert company_news') THEN
        CREATE POLICY "Allow authenticated users to insert company_news" ON company_news FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for company_news insert access';
    END IF;
    
    -- Dividend Announcements policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'dividend_announcements' AND policyname = 'Allow public read access to dividend_announcements') THEN
        CREATE POLICY "Allow public read access to dividend_announcements" ON dividend_announcements FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for dividend_announcements read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'dividend_announcements' AND policyname = 'Allow authenticated users to insert dividend_announcements') THEN
        CREATE POLICY "Allow authenticated users to insert dividend_announcements" ON dividend_announcements FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for dividend_announcements insert access';
    END IF;
    
    -- Earnings Announcements policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'earnings_announcements' AND policyname = 'Allow public read access to earnings_announcements') THEN
        CREATE POLICY "Allow public read access to earnings_announcements" ON earnings_announcements FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for earnings_announcements read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'earnings_announcements' AND policyname = 'Allow authenticated users to insert earnings_announcements') THEN
        CREATE POLICY "Allow authenticated users to insert earnings_announcements" ON earnings_announcements FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for earnings_announcements insert access';
    END IF;
    
    -- ETF Data policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'etf_data' AND policyname = 'Allow public read access to etf_data') THEN
        CREATE POLICY "Allow public read access to etf_data" ON etf_data FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for etf_data read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'etf_data' AND policyname = 'Allow authenticated users to insert etf_data') THEN
        CREATE POLICY "Allow authenticated users to insert etf_data" ON etf_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for etf_data insert access';
    END IF;
    
    -- Corporate Actions policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'corporate_actions' AND policyname = 'Allow public read access to corporate_actions') THEN
        CREATE POLICY "Allow public read access to corporate_actions" ON corporate_actions FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for corporate_actions read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'corporate_actions' AND policyname = 'Allow authenticated users to insert corporate_actions') THEN
        CREATE POLICY "Allow authenticated users to insert corporate_actions" ON corporate_actions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for corporate_actions insert access';
    END IF;
    
    -- Market Sentiment policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_sentiment' AND policyname = 'Allow public read access to market_sentiment') THEN
        CREATE POLICY "Allow public read access to market_sentiment" ON market_sentiment FOR SELECT USING (true);
        RAISE NOTICE 'Created RLS policy for market_sentiment read access';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_sentiment' AND policyname = 'Allow authenticated users to insert market_sentiment') THEN
        CREATE POLICY "Allow authenticated users to insert market_sentiment" ON market_sentiment FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        RAISE NOTICE 'Created RLS policy for market_sentiment insert access';
    END IF;
END $$;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT '🎉 Sky Garden comprehensive database schema setup completed successfully!' as message;
