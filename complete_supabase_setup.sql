-- =============================================================================
-- COMPLETE SUPABASE DATABASE SETUP FOR CASABLANCA INSIGHTS
-- Run this entire script in Supabase SQL Editor
-- =============================================================================

-- 1. CREATE ALL TABLES FIRST
-- =============================================================================

-- Create Companies Table
CREATE TABLE IF NOT EXISTS public.companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Comprehensive Market Data Table
CREATE TABLE IF NOT EXISTS public.comprehensive_market_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    current_price DECIMAL(15,4),
    change_1d DECIMAL(15,4),
    change_1d_percent DECIMAL(8,4),
    open_price DECIMAL(15,4),
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(8,4),
    dividend_yield DECIMAL(8,4),
    fifty_two_week_high DECIMAL(15,4),
    fifty_two_week_low DECIMAL(15,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Company News Table
CREATE TABLE IF NOT EXISTS public.company_news (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP WITH TIME ZONE,
    url VARCHAR(1000),
    category VARCHAR(50),
    sentiment VARCHAR(20),
    impact VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Dividend Announcements Table
CREATE TABLE IF NOT EXISTS public.dividend_announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    type VARCHAR(50),
    amount DECIMAL(15,4),
    currency VARCHAR(3) DEFAULT 'MAD',
    ex_date DATE,
    record_date DATE,
    payment_date DATE,
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Earnings Announcements Table
CREATE TABLE IF NOT EXISTS public.earnings_announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    period VARCHAR(20),
    report_date DATE,
    estimate DECIMAL(15,4),
    actual DECIMAL(15,4),
    surprise DECIMAL(15,4),
    surprise_percent DECIMAL(8,4),
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Market Status Table
CREATE TABLE IF NOT EXISTS public.market_status (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    market_status VARCHAR(20),
    current_time_local TIME,
    trading_hours VARCHAR(50),
    total_market_cap BIGINT,
    total_volume BIGINT,
    advancers INTEGER,
    decliners INTEGER,
    unchanged INTEGER,
    top_gainer JSONB,
    top_loser JSONB,
    most_active JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. CREATE INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON comprehensive_market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_created_at ON comprehensive_market_data(created_at);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_dividend_ticker ON dividend_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_ticker ON earnings_announcements(ticker);

-- 3. ENABLE ROW LEVEL SECURITY
-- =============================================================================

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE comprehensive_market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE dividend_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_status ENABLE ROW LEVEL SECURITY;

-- 4. CREATE RLS POLICIES (PUBLIC READ ACCESS)
-- =============================================================================

DROP POLICY IF EXISTS "Allow public read access on companies" ON public.companies;
CREATE POLICY "Allow public read access on companies"
ON public.companies
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Allow public read access on market_data" ON public.comprehensive_market_data;
CREATE POLICY "Allow public read access on market_data"
ON public.comprehensive_market_data
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Allow public read access on news" ON public.company_news;
CREATE POLICY "Allow public read access on news"
ON public.company_news
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Allow public read access on dividends" ON public.dividend_announcements;
CREATE POLICY "Allow public read access on dividends"
ON public.dividend_announcements
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Allow public read access on earnings" ON public.earnings_announcements;
CREATE POLICY "Allow public read access on earnings"
ON public.earnings_announcements
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Allow public read access on market_status" ON public.market_status;
CREATE POLICY "Allow public read access on market_status"
ON public.market_status
FOR SELECT
USING (true);

-- 5. CREATE RLS POLICIES (SERVICE ROLE FULL ACCESS)
-- =============================================================================

DROP POLICY IF EXISTS "Allow service role full access on companies" ON public.companies;
CREATE POLICY "Allow service role full access on companies"
ON public.companies
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

DROP POLICY IF EXISTS "Allow service role full access on market_data" ON public.comprehensive_market_data;
CREATE POLICY "Allow service role full access on market_data"
ON public.comprehensive_market_data
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

DROP POLICY IF EXISTS "Allow service role full access on news" ON public.company_news;
CREATE POLICY "Allow service role full access on news"
ON public.company_news
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

DROP POLICY IF EXISTS "Allow service role full access on dividends" ON public.dividend_announcements;
CREATE POLICY "Allow service role full access on dividends"
ON public.dividend_announcements
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

DROP POLICY IF EXISTS "Allow service role full access on earnings" ON public.earnings_announcements;
CREATE POLICY "Allow service role full access on earnings"
ON public.earnings_announcements
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

DROP POLICY IF EXISTS "Allow service role full access on market_status" ON public.market_status;
CREATE POLICY "Allow service role full access on market_status"
ON public.market_status
FOR ALL
USING ((auth.jwt() ->> 'role') = 'service_role')
WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

-- =============================================================================
-- SETUP COMPLETE! 
-- Tables created, indexes added, RLS enabled, policies configured
-- Ready for automatic Airflow population!
-- =============================================================================
