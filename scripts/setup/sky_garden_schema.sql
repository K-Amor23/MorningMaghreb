-- Sky Garden Comprehensive Database Schema
-- Run this script in your Supabase dashboard SQL editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Market Status Table
CREATE TABLE IF NOT EXISTS market_status (
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

-- 2. Comprehensive Market Data Table
CREATE TABLE IF NOT EXISTS comprehensive_market_data (
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

-- 3. Company News Table
CREATE TABLE IF NOT EXISTS company_news (
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

-- 4. Dividend Announcements Table
CREATE TABLE IF NOT EXISTS dividend_announcements (
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

-- 5. Earnings Announcements Table
CREATE TABLE IF NOT EXISTS earnings_announcements (
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

-- 6. ETF Data Table
CREATE TABLE IF NOT EXISTS etf_data (
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

-- 7. Corporate Actions Table
CREATE TABLE IF NOT EXISTS corporate_actions (
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

-- 8. Market Sentiment Table
CREATE TABLE IF NOT EXISTS market_sentiment (
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_ticker ON comprehensive_market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_sector ON comprehensive_market_data(sector);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_scraped_at ON comprehensive_market_data(scraped_at);

CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_category ON company_news(category);

CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ticker ON dividend_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ex_date ON dividend_announcements(ex_date);

CREATE INDEX IF NOT EXISTS idx_earnings_announcements_ticker ON earnings_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_report_date ON earnings_announcements(report_date);

CREATE INDEX IF NOT EXISTS idx_etf_data_ticker ON etf_data(ticker);
CREATE INDEX IF NOT EXISTS idx_etf_data_asset_class ON etf_data(asset_class);

CREATE INDEX IF NOT EXISTS idx_corporate_actions_ticker ON corporate_actions(ticker);
CREATE INDEX IF NOT EXISTS idx_corporate_actions_action_type ON corporate_actions(action_type);

CREATE INDEX IF NOT EXISTS idx_market_sentiment_ticker ON market_sentiment(ticker);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables
CREATE TRIGGER update_market_status_updated_at BEFORE UPDATE ON market_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comprehensive_market_data_updated_at BEFORE UPDATE ON comprehensive_market_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_company_news_updated_at BEFORE UPDATE ON company_news FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dividend_announcements_updated_at BEFORE UPDATE ON dividend_announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_earnings_announcements_updated_at BEFORE UPDATE ON earnings_announcements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_etf_data_updated_at BEFORE UPDATE ON etf_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_corporate_actions_updated_at BEFORE UPDATE ON corporate_actions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_market_sentiment_updated_at BEFORE UPDATE ON market_sentiment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
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
) ON CONFLICT DO NOTHING;

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
) ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE market_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE comprehensive_market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE dividend_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE etf_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE corporate_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_sentiment ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access
CREATE POLICY "Allow public read access to market_status" ON market_status FOR SELECT USING (true);
CREATE POLICY "Allow public read access to comprehensive_market_data" ON comprehensive_market_data FOR SELECT USING (true);
CREATE POLICY "Allow public read access to company_news" ON company_news FOR SELECT USING (true);
CREATE POLICY "Allow public read access to dividend_announcements" ON dividend_announcements FOR SELECT USING (true);
CREATE POLICY "Allow public read access to earnings_announcements" ON earnings_announcements FOR SELECT USING (true);
CREATE POLICY "Allow public read access to etf_data" ON etf_data FOR SELECT USING (true);
CREATE POLICY "Allow public read access to corporate_actions" ON corporate_actions FOR SELECT USING (true);
CREATE POLICY "Allow public read access to market_sentiment" ON market_sentiment FOR SELECT USING (true);

-- Create RLS policies for authenticated users to insert/update
CREATE POLICY "Allow authenticated users to insert market_status" ON market_status FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert comprehensive_market_data" ON comprehensive_market_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert company_news" ON company_news FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert dividend_announcements" ON dividend_announcements FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert earnings_announcements" ON earnings_announcements FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert etf_data" ON etf_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert corporate_actions" ON corporate_actions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated users to insert market_sentiment" ON market_sentiment FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT '🎉 Sky Garden comprehensive database schema created successfully!' as message;
