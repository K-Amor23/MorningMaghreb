-- Comprehensive Market Data Schema for Enhanced Frontend
-- This schema supports all the data needed for the enhanced frontend components

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Market Status Table
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

-- Create index on scraped_at for time-series queries
CREATE INDEX IF NOT EXISTS idx_market_status_scraped_at ON market_status(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('market_status', 'scraped_at', if_not_exists => TRUE);

-- Comprehensive Market Data Table
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

-- Create indexes for comprehensive market data
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_ticker ON comprehensive_market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_scraped_at ON comprehensive_market_data(scraped_at);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_sector ON comprehensive_market_data(sector);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_change_percent ON comprehensive_market_data(change_percent);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_volume ON comprehensive_market_data(volume);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_market_cap ON comprehensive_market_data(market_cap);

-- Convert to hypertable for time-series data
SELECT create_hypertable('comprehensive_market_data', 'scraped_at', if_not_exists => TRUE);

-- Company News Table
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

-- Create indexes for company news
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_category ON company_news(category);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_scraped_at ON company_news(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('company_news', 'scraped_at', if_not_exists => TRUE);

-- Dividend Announcements Table
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

-- Create indexes for dividend announcements
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ticker ON dividend_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_ex_date ON dividend_announcements(ex_date);
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_status ON dividend_announcements(status);
CREATE INDEX IF NOT EXISTS idx_dividend_announcements_scraped_at ON dividend_announcements(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('dividend_announcements', 'scraped_at', if_not_exists => TRUE);

-- Earnings Announcements Table
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

-- Create indexes for earnings announcements
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_ticker ON earnings_announcements(ticker);
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_report_date ON earnings_announcements(report_date);
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_status ON earnings_announcements(status);
CREATE INDEX IF NOT EXISTS idx_earnings_announcements_scraped_at ON earnings_announcements(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('earnings_announcements', 'scraped_at', if_not_exists => TRUE);

-- ETF Data Table
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

-- Create indexes for ETF data
CREATE INDEX IF NOT EXISTS idx_etf_data_ticker ON etf_data(ticker);
CREATE INDEX IF NOT EXISTS idx_etf_data_asset_class ON etf_data(asset_class);
CREATE INDEX IF NOT EXISTS idx_etf_data_scraped_at ON etf_data(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('etf_data', 'scraped_at', if_not_exists => TRUE);

-- Corporate Actions Table
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

-- Create indexes for corporate actions
CREATE INDEX IF NOT EXISTS idx_corporate_actions_ticker ON corporate_actions(ticker);
CREATE INDEX IF NOT EXISTS idx_corporate_actions_action_type ON corporate_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_corporate_actions_announcement_date ON corporate_actions(announcement_date);
CREATE INDEX IF NOT EXISTS idx_corporate_actions_status ON corporate_actions(status);
CREATE INDEX IF NOT EXISTS idx_corporate_actions_scraped_at ON corporate_actions(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('corporate_actions', 'scraped_at', if_not_exists => TRUE);

-- Market Sentiment Table
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

-- Create indexes for market sentiment
CREATE INDEX IF NOT EXISTS idx_market_sentiment_ticker ON market_sentiment(ticker);
CREATE INDEX IF NOT EXISTS idx_market_sentiment_sentiment_score ON market_sentiment(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_market_sentiment_scraped_at ON market_sentiment(scraped_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('market_sentiment', 'scraped_at', if_not_exists => TRUE);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_comprehensive_market_data_updated_at 
    BEFORE UPDATE ON comprehensive_market_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_status_updated_at 
    BEFORE UPDATE ON market_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_news_updated_at 
    BEFORE UPDATE ON company_news 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dividend_announcements_updated_at 
    BEFORE UPDATE ON dividend_announcements 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_earnings_announcements_updated_at 
    BEFORE UPDATE ON earnings_announcements 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etf_data_updated_at 
    BEFORE UPDATE ON etf_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_corporate_actions_updated_at 
    BEFORE UPDATE ON corporate_actions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_sentiment_updated_at 
    BEFORE UPDATE ON market_sentiment 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
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

-- Create materialized views for performance
CREATE MATERIALIZED VIEW IF NOT EXISTS market_summary_mv AS
SELECT 
    COUNT(DISTINCT ticker) as total_companies,
    AVG(change_percent) as market_avg_change,
    SUM(CASE WHEN change_percent > 0 THEN 1 ELSE 0 END) as total_advancers,
    SUM(CASE WHEN change_percent < 0 THEN 1 ELSE 0 END) as total_decliners,
    SUM(CASE WHEN change_percent = 0 THEN 1 ELSE 0 END) as total_unchanged,
    AVG(volume) as avg_volume,
    SUM(market_cap) as total_market_cap,
    MAX(scraped_at) as last_update
FROM comprehensive_market_data
WHERE scraped_at = (
    SELECT MAX(scraped_at) 
    FROM comprehensive_market_data
);

-- Create indexes on materialized view
CREATE INDEX IF NOT EXISTS idx_market_summary_mv_last_update ON market_summary_mv(last_update);

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_role;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO admin_role;

-- Insert sample data for testing
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

-- Create a function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_market_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW market_summary_mv;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get comprehensive data for a ticker
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

-- Create a function to get market overview
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_price_change ON comprehensive_market_data(change_percent);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_high_low ON comprehensive_market_data(high, low);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_pe_ratio ON comprehensive_market_data(pe_ratio);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_dividend_yield ON comprehensive_market_data(dividend_yield);

-- Create composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_ticker_scraped ON comprehensive_market_data(ticker, scraped_at);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_sector_change ON comprehensive_market_data(sector, change_percent);
CREATE INDEX IF NOT EXISTS idx_comprehensive_market_data_volume_price ON comprehensive_market_data(volume, current_price);

-- Add comments for documentation
COMMENT ON TABLE comprehensive_market_data IS 'Comprehensive market data for all listed companies including technical and fundamental metrics';
COMMENT ON TABLE market_status IS 'Real-time market status and key metrics for the Casablanca Stock Exchange';
COMMENT ON TABLE company_news IS 'Company news, announcements, and corporate communications';
COMMENT ON TABLE dividend_announcements IS 'Dividend announcements, stock splits, and other distributions';
COMMENT ON TABLE earnings_announcements IS 'Earnings calendar, estimates, and actual results';
COMMENT ON TABLE etf_data IS 'ETF information including holdings, allocations, and performance metrics';
COMMENT ON TABLE corporate_actions IS 'Major corporate events like mergers, acquisitions, and restructuring';
COMMENT ON TABLE market_sentiment IS 'Market sentiment analysis and scoring';

COMMENT ON FUNCTION get_comprehensive_ticker_data IS 'Get comprehensive data for a specific ticker including market data, news, dividends, and earnings';
COMMENT ON FUNCTION get_market_overview IS 'Get comprehensive market overview including top movers, sector performance, and upcoming events';
COMMENT ON FUNCTION refresh_market_views IS 'Refresh materialized views for better performance';
