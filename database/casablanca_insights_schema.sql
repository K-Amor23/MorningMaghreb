-- Casablanca Insights Database Schema for Supabase
-- Complete schema for financial data, news, and sentiment analysis

-- ============================================
-- CORE COMPANY DATA TABLES
-- ============================================

-- Companies table (master company information)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap_billion DECIMAL(10,2),
    price DECIMAL(10,2),
    change_1d_percent DECIMAL(5,2),
    change_ytd_percent DECIMAL(5,2),
    size_category VARCHAR(20) CHECK (size_category IN ('Micro Cap', 'Small Cap', 'Mid Cap', 'Large Cap')),
    sector_group VARCHAR(100),
    exchange VARCHAR(100) DEFAULT 'Casablanca Stock Exchange (BVC)',
    country VARCHAR(50) DEFAULT 'Morocco',
    company_url TEXT,
    ir_url TEXT,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Company Prices table (OHLCV data)
CREATE TABLE IF NOT EXISTS company_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
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

-- Company Reports table (financial reports)
CREATE TABLE IF NOT EXISTS company_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    report_type VARCHAR(50) CHECK (report_type IN ('annual_report', 'quarterly_report', 'financial_statement', 'earnings', 'unknown')),
    report_date VARCHAR(50),
    report_year VARCHAR(4),
    report_quarter VARCHAR(10),
    url TEXT NOT NULL,
    filename VARCHAR(255),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, url)
);

-- Company News table (news and sentiment)
CREATE TABLE IF NOT EXISTS company_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
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

-- ============================================
-- ANALYTICS AND SIGNALS TABLES
-- ============================================

-- Analytics Signals table (technical indicators and signals)
CREATE TABLE IF NOT EXISTS analytics_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    signal_date DATE NOT NULL,
    signal_type VARCHAR(50) CHECK (signal_type IN ('buy', 'sell', 'hold', 'strong_buy', 'strong_sell')),
    indicator VARCHAR(50) CHECK (indicator IN ('rsi', 'macd', 'moving_average', 'volume', 'sentiment', 'earnings')),
    value DECIMAL(10,4),
    threshold DECIMAL(10,4),
    confidence DECIMAL(3,2),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, signal_date, indicator)
);

-- Market Summary table (aggregated market data)
CREATE TABLE IF NOT EXISTS market_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE UNIQUE NOT NULL,
    masi_index DECIMAL(10,2),
    masi_change_percent DECIMAL(5,2),
    madasi_index DECIMAL(10,2),
    madasi_change_percent DECIMAL(5,2),
    total_volume BIGINT,
    advancing_stocks INTEGER,
    declining_stocks INTEGER,
    unchanged_stocks INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SENTIMENT VOTING SYSTEM TABLES
-- ============================================

-- Sentiment Votes Table (User sentiment votes)
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Will reference auth.users(id) in Supabase
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
    confidence INTEGER NOT NULL DEFAULT 3 CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Sentiment Aggregates Table (Computed sentiment statistics)
CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL UNIQUE,
    bullish_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    bearish_count INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    bullish_percentage DECIMAL(5,2) DEFAULT 0.0,
    neutral_percentage DECIMAL(5,2) DEFAULT 0.0,
    bearish_percentage DECIMAL(5,2) DEFAULT 0.0,
    average_confidence DECIMAL(3,2) DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- NEWSLETTER SYSTEM TABLES
-- ============================================

-- Newsletter Subscribers
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

-- Newsletter Campaigns
CREATE TABLE IF NOT EXISTS newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en' CHECK (language IN ('en', 'fr', 'ar')),
    campaign_type VARCHAR(50) DEFAULT 'weekly_recap' CHECK (campaign_type IN ('weekly_recap', 'market_alert', 'custom')),
    sent_at TIMESTAMPTZ,
    recipient_count INTEGER,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_size_category ON companies(size_category);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Company Prices indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

-- Company Reports indexes
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker ON company_reports(ticker);
CREATE INDEX IF NOT EXISTS idx_company_reports_type ON company_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_company_reports_year ON company_reports(report_year);
CREATE INDEX IF NOT EXISTS idx_company_reports_scraped_at ON company_reports(scraped_at);

-- Company News indexes
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

-- Analytics Signals indexes
CREATE INDEX IF NOT EXISTS idx_analytics_signals_ticker ON analytics_signals(ticker);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_date ON analytics_signals(signal_date);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_type ON analytics_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_indicator ON analytics_signals(indicator);

-- Market Summary indexes
CREATE INDEX IF NOT EXISTS idx_market_summary_date ON market_summary(date);

-- Sentiment indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);

-- Newsletter indexes
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_status ON newsletter_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_type ON newsletter_campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_sent_at ON newsletter_campaigns(sent_at);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update sentiment aggregates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert sentiment aggregate
    INSERT INTO sentiment_aggregates (ticker, bullish_count, neutral_count, bearish_count, total_votes, 
                                     bullish_percentage, neutral_percentage, bearish_percentage, average_confidence, last_updated)
    SELECT 
        ticker,
        COUNT(CASE WHEN sentiment = 'bullish' THEN 1 END) as bullish_count,
        COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral_count,
        COUNT(CASE WHEN sentiment = 'bearish' THEN 1 END) as bearish_count,
        COUNT(*) as total_votes,
        ROUND(COUNT(CASE WHEN sentiment = 'bullish' THEN 1 END) * 100.0 / COUNT(*), 2) as bullish_percentage,
        ROUND(COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) * 100.0 / COUNT(*), 2) as neutral_percentage,
        ROUND(COUNT(CASE WHEN sentiment = 'bearish' THEN 1 END) * 100.0 / COUNT(*), 2) as bearish_percentage,
        ROUND(AVG(confidence), 2) as average_confidence,
        NOW() as last_updated
    FROM sentiment_votes
    WHERE ticker = COALESCE(NEW.ticker, OLD.ticker)
    GROUP BY ticker
    ON CONFLICT (ticker) DO UPDATE SET
        bullish_count = EXCLUDED.bullish_count,
        neutral_count = EXCLUDED.neutral_count,
        bearish_count = EXCLUDED.bearish_count,
        total_votes = EXCLUDED.total_votes,
        bullish_percentage = EXCLUDED.bullish_percentage,
        neutral_percentage = EXCLUDED.neutral_percentage,
        bearish_percentage = EXCLUDED.bearish_percentage,
        average_confidence = EXCLUDED.average_confidence,
        last_updated = EXCLUDED.last_updated;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for sentiment votes
CREATE TRIGGER sentiment_votes_insert_trigger
    AFTER INSERT ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

CREATE TRIGGER sentiment_votes_update_trigger
    AFTER UPDATE ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

CREATE TRIGGER sentiment_votes_delete_trigger
    AFTER DELETE ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

-- Triggers for updated_at columns
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sentiment_votes_updated_at 
    BEFORE UPDATE ON sentiment_votes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Top Bullish Stocks View
CREATE OR REPLACE VIEW top_bullish_stocks AS
SELECT 
    c.ticker,
    c.name,
    c.sector,
    sa.bullish_percentage,
    sa.total_votes,
    sa.average_confidence,
    cp.close as current_price,
    cp.change_1d_percent
FROM companies c
LEFT JOIN sentiment_aggregates sa ON c.ticker = sa.ticker
LEFT JOIN company_prices cp ON c.ticker = cp.ticker 
    AND cp.date = (SELECT MAX(date) FROM company_prices WHERE ticker = c.ticker)
WHERE c.is_active = TRUE
ORDER BY sa.bullish_percentage DESC NULLS LAST, sa.total_votes DESC;

-- Top Bearish Stocks View
CREATE OR REPLACE VIEW top_bearish_stocks AS
SELECT 
    c.ticker,
    c.name,
    c.sector,
    sa.bearish_percentage,
    sa.total_votes,
    sa.average_confidence,
    cp.close as current_price,
    cp.change_1d_percent
FROM companies c
LEFT JOIN sentiment_aggregates sa ON c.ticker = sa.ticker
LEFT JOIN company_prices cp ON c.ticker = cp.ticker 
    AND cp.date = (SELECT MAX(date) FROM company_prices WHERE ticker = c.ticker)
WHERE c.is_active = TRUE
ORDER BY sa.bearish_percentage DESC NULLS LAST, sa.total_votes DESC;

-- Latest News View
CREATE OR REPLACE VIEW latest_news AS
SELECT 
    cn.ticker,
    c.name as company_name,
    cn.headline,
    cn.source,
    cn.published_at,
    cn.sentiment,
    cn.sentiment_score,
    cn.url
FROM company_news cn
JOIN companies c ON cn.ticker = c.ticker
WHERE cn.published_at >= NOW() - INTERVAL '7 days'
ORDER BY cn.published_at DESC;

-- Company Summary View
CREATE OR REPLACE VIEW company_summary AS
SELECT 
    c.ticker,
    c.name,
    c.sector,
    c.market_cap_billion,
    cp.close as current_price,
    cp.change_1d_percent,
    cp.change_ytd_percent,
    sa.bullish_percentage,
    sa.bearish_percentage,
    sa.total_votes,
    COUNT(cn.id) as news_count_7d,
    COUNT(cr.id) as reports_count
FROM companies c
LEFT JOIN company_prices cp ON c.ticker = cp.ticker 
    AND cp.date = (SELECT MAX(date) FROM company_prices WHERE ticker = c.ticker)
LEFT JOIN sentiment_aggregates sa ON c.ticker = sa.ticker
LEFT JOIN company_news cn ON c.ticker = cn.ticker 
    AND cn.published_at >= NOW() - INTERVAL '7 days'
LEFT JOIN company_reports cr ON c.ticker = cr.ticker
WHERE c.is_active = TRUE
GROUP BY c.ticker, c.name, c.sector, c.market_cap_billion, cp.close, cp.change_1d_percent, 
         cp.change_ytd_percent, sa.bullish_percentage, sa.bearish_percentage, sa.total_votes;

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on tables that need it
ALTER TABLE sentiment_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

-- Sentiment votes policies (users can only see their own votes)
CREATE POLICY "Users can view their own sentiment votes" ON sentiment_votes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sentiment votes" ON sentiment_votes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own sentiment votes" ON sentiment_votes
    FOR UPDATE USING (auth.uid() = user_id);

-- Newsletter subscribers policies (public read, authenticated insert)
CREATE POLICY "Anyone can view newsletter subscribers" ON newsletter_subscribers
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can subscribe" ON newsletter_subscribers
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- ============================================
-- SAMPLE DATA INSERTION (Optional)
-- ============================================

-- Insert sample companies (you can uncomment and modify as needed)
/*
INSERT INTO companies (ticker, name, sector, market_cap_billion, size_category) VALUES
('ATW', 'Attijariwafa Bank', 'Financials', 45.2, 'Large Cap'),
('IAM', 'Maroc Telecom', 'Telecommunications', 38.7, 'Large Cap'),
('BCP', 'Banque Centrale Populaire', 'Financials', 32.1, 'Large Cap'),
('GAZ', 'Afriquia Gaz', 'Oil & Gas', 15.1, 'Mid Cap'),
('MNG', 'Managem', 'Materials', 12.8, 'Mid Cap')
ON CONFLICT (ticker) DO NOTHING;
*/

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE companies IS 'Master table for all Moroccan companies listed on the Casablanca Stock Exchange';
COMMENT ON TABLE company_prices IS 'Daily OHLCV price data for all companies';
COMMENT ON TABLE company_reports IS 'Financial reports and documents scraped from company IR pages';
COMMENT ON TABLE company_news IS 'News articles and sentiment analysis for companies';
COMMENT ON TABLE analytics_signals IS 'Technical analysis signals and indicators';
COMMENT ON TABLE sentiment_votes IS 'User sentiment votes for companies';
COMMENT ON TABLE sentiment_aggregates IS 'Aggregated sentiment statistics for companies';
COMMENT ON TABLE newsletter_subscribers IS 'Newsletter subscription management';
COMMENT ON TABLE newsletter_campaigns IS 'Newsletter campaign tracking'; 