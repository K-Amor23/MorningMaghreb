-- Create missing tables for frontend data flow
-- Run this in your Supabase SQL Editor

-- 1. Comprehensive Market Data Table
CREATE TABLE IF NOT EXISTS comprehensive_market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    current_price DECIMAL(12,4),
    change DECIMAL(12,4),
    change_percent DECIMAL(8,6),
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    volume BIGINT,
    market_cap DECIMAL(20,2),
    pe_ratio DECIMAL(10,4),
    dividend_yield DECIMAL(8,6),
    roe DECIMAL(8,6),
    shares_outstanding BIGINT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Company News Table
CREATE TABLE IF NOT EXISTS company_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source VARCHAR(255),
    published_at TIMESTAMPTZ,
    url TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    impact_level VARCHAR(20) CHECK (impact_level IN ('low', 'medium', 'high')),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Dividend Announcements Table
CREATE TABLE IF NOT EXISTS dividend_announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    amount DECIMAL(8,4),
    ex_date DATE,
    payment_date DATE,
    dividend_status VARCHAR(20) DEFAULT 'announced',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Earnings Announcements Table
CREATE TABLE IF NOT EXISTS earnings_announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    period VARCHAR(20),
    estimate DECIMAL(8,4),
    actual DECIMAL(8,4),
    surprise DECIMAL(8,4),
    surprise_percent DECIMAL(8,6),
    earnings_status VARCHAR(20) DEFAULT 'scheduled',
    report_date DATE,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Market Status Table
CREATE TABLE IF NOT EXISTS market_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_status VARCHAR(20) DEFAULT 'open',
    current_time TIME,
    trading_hours VARCHAR(50),
    total_market_cap DECIMAL(20,2),
    total_volume DECIMAL(20,2),
    advancers INTEGER,
    decliners INTEGER,
    unchanged INTEGER,
    top_gainer JSONB,
    top_loser JSONB,
    most_active JSONB,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_ticker ON comprehensive_market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_scraped_at ON comprehensive_market_data(scraped_at);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ticker ON dividend_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_ticker ON earnings_announcements(ticker);

-- Enable Row Level Security (RLS)
ALTER TABLE comprehensive_market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE dividend_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_status ENABLE ROW LEVEL SECURITY;

-- Create public read policies
CREATE POLICY "Allow public read access to market data" ON comprehensive_market_data
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to news" ON company_news
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to dividends" ON dividend_announcements
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to earnings" ON earnings_announcements
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to market status" ON market_status
    FOR SELECT USING (true);
