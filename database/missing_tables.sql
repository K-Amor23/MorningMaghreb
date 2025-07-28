-- Missing Tables SQL for Supabase
-- Run this in your Supabase SQL Editor to create the missing tables

-- Create company_prices table
CREATE TABLE IF NOT EXISTS company_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    adjusted_close DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);

-- Create company_news table
CREATE TABLE IF NOT EXISTS company_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    headline TEXT NOT NULL,
    source VARCHAR(255),
    published_at TIMESTAMPTZ,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    sentiment_score DECIMAL(3,2),
    url TEXT,
    content_preview TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, url, published_at)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE company_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow public read access to company_prices" ON company_prices
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to company_news" ON company_news
    FOR SELECT USING (true);

-- Grant permissions
GRANT ALL ON company_prices TO anon, authenticated;
GRANT ALL ON company_news TO anon, authenticated; 